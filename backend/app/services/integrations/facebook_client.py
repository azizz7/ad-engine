import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi

from app.core.config import settings

logger = logging.getLogger(__name__)


class FacebookClient:
    def __init__(self):
        self.access_token = settings.fb_access_token
        self.ad_account_id = settings.fb_ad_account_id
        self.app_id = settings.fb_app_id
        self.app_secret = settings.fb_app_secret

        self.is_configured = bool(self.access_token and self.ad_account_id)

        if self.is_configured:
            try:
                FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            except Exception:
                logger.exception("Failed to initialize Facebook Ads API client")
                self.is_configured = False

    def get_campaign_insights(self, days: int = 30) -> Optional[pd.DataFrame]:
        if not self.is_configured:
            logger.warning("Facebook API not configured; skipping fetch")
            return None

        try:
            account = AdAccount(self.ad_account_id)

            fields = [
                AdsInsights.Field.date_start,
                AdsInsights.Field.campaign_name,
                AdsInsights.Field.adset_name,
                AdsInsights.Field.ad_name,
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.actions,
            ]

            params = {
                "level": "ad",
                "time_range": {
                    "since": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                    "until": datetime.now().strftime("%Y-%m-%d"),
                },
                "time_increment": 1,
            }

            insights = account.get_insights(fields=fields, params=params)

            data = []
            for item in insights:
                conversions = 0
                if "actions" in item:
                    for action in item["actions"]:
                        if action["action_type"] in ["purchase", "lead", "omni_purchase"]:
                            conversions += int(action["value"])

                spend = float(item.get("spend", 0))
                revenue = 0.0
                if "action_values" in item:
                    for val in item["action_values"]:
                        if val["action_type"] in ["purchase", "omni_purchase"]:
                            revenue += float(val["value"])

                data.append(
                    {
                        "date": item["date_start"],
                        "campaign_name": item["campaign_name"],
                        "ad_group": item.get("adset_name", "Unknown"),
                        "ad_name": item.get("ad_name", "Unknown"),
                        "impressions": int(item.get("impressions", 0)),
                        "clicks": int(item.get("clicks", 0)),
                        "spend": spend,
                        "conversions": conversions,
                        "revenue": revenue,
                    }
                )

            return pd.DataFrame(data) if data else pd.DataFrame()

        except Exception:
            logger.exception("Error fetching Facebook Ads data")
            return None
