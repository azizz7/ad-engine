from app.services.ai_narrative import generate_ai_summary


def test_returns_none_without_api_key_and_makes_no_network_call(monkeypatch):
    """This is the default state for anyone who hasn't configured
    ANTHROPIC_API_KEY - it must be a fast, safe no-op, never an error."""
    monkeypatch.setattr("app.services.ai_narrative.settings.anthropic_api_key", None)
    monkeypatch.setattr("app.services.ai_narrative._client", None)

    result = generate_ai_summary({"roas": 2.0}, ["Some insight"])
    assert result is None
