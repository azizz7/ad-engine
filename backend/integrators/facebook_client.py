from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from datetime import datetime, timedelta
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class FacebookClient:
    def __init__(self):
        self.access_token = os.getenv("FB_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("FB_AD_ACCOUNT_ID")
        self.app_id = os.getenv("FB_APP_ID")
        self.app_secret = os.getenv("FB_APP_SECRET")
        
        self.is_configured = all([self.access_token, self.ad_account_id])
        
        if self.is_configured:
            try:
                FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            except Exception as e:
                print(f"Failed to init Facebook API: {e}")
                self.is_configured = False

    def get_campaign_insights(self, days=30):
        if not self.is_configured:
            print("Facebook API not configured.")
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
                AdsInsights.Field.actions, # For conversion parsing
            ]
            
            params = {
                'level': 'ad',
                'time_range': {
                    'since': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                    'until': datetime.now().strftime('%Y-%m-%d'),
                },
                'time_increment': 1, # Daily breakdown
            }
            
            insights = account.get_insights(fields=fields, params=params)
            
            data = []
            for item in insights:
                # Parse conversions (actions can be many things)
                conversions = 0
                if 'actions' in item:
                    for action in item['actions']:
                        # Count purchase or lead events as conversions
                        if action['action_type'] in ['purchase', 'lead', 'omni_purchase']:
                            conversions += int(action['value'])
                
                spend = float(item.get('spend', 0))
                revenue = 0 # Revenue tracking requires 'action_values' parsing, omitted for MVP simplicity
                
                # Approximate revenue if not available (Mock behavior for demo if real revenue is 0)
                # In real app, we would parse action_values['offsite_conversion.fb_pixel_purchase']
                if 'action_values' in item:
                    for val in item['action_values']:
                         if val['action_type'] in ['purchase', 'omni_purchase']:
                             revenue += float(val['value'])

                data.append({
                    'date': item['date_start'],
                    'campaign_name': item['campaign_name'],
                    'ad_group': item.get('adset_name', 'Unknown'),
                    'ad_name': item.get('ad_name', 'Unknown'),
                    'impressions': int(item.get('impressions', 0)),
                    'clicks': int(item.get('clicks', 0)),
                    'spend': spend,
                    'conversions': conversions,
                    'revenue': revenue
                })

            if not data:
                return pd.DataFrame()

            return pd.DataFrame(data)

        except Exception as e:
            print(f"Error fetching FB data: {e}")
            return None
