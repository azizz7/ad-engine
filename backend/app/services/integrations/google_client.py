import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from google.ads.googleads.client import GoogleAdsClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleClient:
    def __init__(self):
        self.developer_token = settings.google_ads_developer_token
        self.client_id = settings.google_ads_client_id
        self.client_secret = settings.google_ads_client_secret
        self.refresh_token = settings.google_ads_refresh_token
        self.login_customer_id = settings.google_ads_login_customer_id
        self.customer_id = settings.google_ads_customer_id

        self.is_configured = all(
            [
                self.developer_token,
                self.client_id,
                self.client_secret,
                self.refresh_token,
                self.customer_id,
            ]
        )

    def get_campaign_insights(self, days: int = 30) -> Optional[pd.DataFrame]:
        if not self.is_configured:
            logger.warning("Google Ads API not configured; skipping fetch")
            return None

        try:
            credentials = {
                "developer_token": self.developer_token,
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "login_customer_id": self.login_customer_id,
                "use_proto_plus": True,
            }

            client = GoogleAdsClient.load_from_dict(credentials)
            ga_service = client.get_service("GoogleAdsService")

            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")

            query = f"""
                SELECT
                    segments.date,
                    campaign.name,
                    ad_group.name,
                    ad_group_ad.ad.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value
                FROM ad_group_ad
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            """

            stream = ga_service.search_stream(customer_id=self.customer_id, query=query)

            data = []
            for batch in stream:
                for row in batch:
                    spend = row.metrics.cost_micros / 1_000_000.0
                    data.append(
                        {
                            "date": row.segments.date,
                            "campaign_name": row.campaign.name,
                            "ad_group": row.ad_group.name,
                            "ad_name": row.ad_group_ad.ad.name or "Unknown Ad",
                            "impressions": row.metrics.impressions,
                            "clicks": row.metrics.clicks,
                            "spend": round(spend, 2),
                            "conversions": row.metrics.conversions,
                            "revenue": round(row.metrics.conversions_value, 2),
                        }
                    )

            return pd.DataFrame(data) if data else pd.DataFrame()

        except Exception:
            logger.exception("Error fetching Google Ads data")
            return None
