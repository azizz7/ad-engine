"""
Optional LLM-generated executive summary layered on top of the deterministic
rule-based insights.

This is intentionally opt-in and fails soft: it only runs if `ANTHROPIC_API_KEY`
is configured, is called at most once per dataset ingestion (never per page
view - the result is cached alongside the rest of the insights), has a short
timeout, and any failure (missing key, network error, bad response) simply
means `None` is returned so the dataset is never blocked or degraded by it.
The rule-based insights always exist independently of this.
"""
import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None and settings.anthropic_api_key:
        import anthropic

        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def generate_ai_summary(
    overall_metrics: Dict[str, Any], rule_based_insights: List[str]
) -> Optional[str]:
    """Return a short (2-4 sentence) plain-English executive summary, or
    None if AI enhancement isn't configured or the call fails."""
    client = _get_client()
    if client is None:
        return None

    bullet_points = "\n".join(f"- {insight}" for insight in rule_based_insights[:8])
    prompt = (
        "You are a marketing analyst. Given these computed ad performance metrics "
        "and auto-generated observations, write a single short executive summary "
        "(2-4 sentences, plain English, no markdown, no bullet points) that a busy "
        "marketing manager could read in five seconds to know what matters most "
        "right now and what to do next.\n\n"
        f"Overall metrics: {overall_metrics}\n\n"
        f"Observations:\n{bullet_points}"
    )

    try:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=200,
            timeout=10.0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        return text or None
    except Exception:
        logger.exception("AI summary generation failed; continuing without it")
        return None
