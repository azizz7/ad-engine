from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class GoogleClient:
    def __init__(self):
        self.developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
        self.client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
        self.refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
        self.login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        self.customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        
        self.is_configured = all([
            self.developer_token, self.client_id, self.client_secret, 
            self.refresh_token, self.customer_id
        ])

    def get_campaign_insights(self, days=30):
        if not self.is_configured:
            print("Google Ads API not configured.")
            return None

        try:
            credentials = {
                "developer_token": self.developer_token,
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "login_customer_id": self.login_customer_id,
                "use_proto_plus": True
            }
            
            client = GoogleAdsClient.load_from_dict(credentials)
            ga_service = client.get_service("GoogleAdsService")
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Query for daily ad performance
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
                    spend = row.metrics.cost_micros / 1000000.0
                    data.append({
                        'date': row.segments.date,
                        'campaign_name': row.campaign.name,
                        'ad_group': row.ad_group.name,
                        'ad_name': row.ad_group_ad.ad.name or "Unknown Ad",
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'spend': round(spend, 2),
                        'conversions': row.metrics.conversions,
                        'revenue': round(row.metrics.conversions_value, 2)
                    })
            
            if not data:
                return pd.DataFrame()
                
            return pd.DataFrame(data)

        except Exception as e:
            print(f"Error fetching Google Ads data: {e}")
            return None
