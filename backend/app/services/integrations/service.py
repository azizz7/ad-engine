"""Fetch (or simulate) ad platform data for the integration-sync endpoints."""
import logging

import pandas as pd

from app.services.integrations.facebook_client import FacebookClient
from app.services.integrations.google_client import GoogleClient
from app.services.integrations.mock_data import generate_mock_facebook_data, generate_mock_google_data

logger = logging.getLogger(__name__)


def fetch_or_mock_facebook_data(days: int = 30, use_mock: bool = False) -> pd.DataFrame:
    """
    Fetch Facebook data. If `use_mock`, return generated demo data immediately.
    Otherwise try the real API; an empty/error result returns an empty DataFrame
    rather than silently falling back to mock data.
    """
    if use_mock:
        logger.info("Demo mode: generating Facebook mock data")
        return generate_mock_facebook_data(days)

    client = FacebookClient()
    if not client.is_configured:
        logger.warning("Facebook API not configured")
        return pd.DataFrame()

    df = client.get_campaign_insights(days=days)
    if df is None or df.empty:
        logger.info("Connected to Facebook, but no data found")
        return pd.DataFrame()

    return df


def fetch_or_mock_google_data(days: int = 30, use_mock: bool = False) -> pd.DataFrame:
    """
    Fetch Google Ads data. If `use_mock`, return generated demo data immediately.
    Otherwise try the real API; an empty/error result returns an empty DataFrame
    rather than silently falling back to mock data.
    """
    if use_mock:
        logger.info("Demo mode: generating Google Ads mock data")
        return generate_mock_google_data(days)

    client = GoogleClient()
    if not client.is_configured:
        logger.warning("Google Ads API not configured")
        return pd.DataFrame()

    df = client.get_campaign_insights(days=days)
    if df is None or df.empty:
        logger.info("Connected to Google, but no data found")
        return pd.DataFrame()

    return df
