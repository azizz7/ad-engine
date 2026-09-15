"""Realistic mock data generators used for demo/simulation mode."""
from datetime import datetime

import numpy as np
import pandas as pd


def generate_mock_facebook_data(days: int = 30) -> pd.DataFrame:
    """Generate realistic mock data for Facebook Ads."""
    dates = pd.date_range(end=datetime.now(), periods=days)
    data = []

    campaigns = [
        "Retargeting_Cart_Abandoners",
        "Prospecting_Lookalike_1%",
        "Brand_Awareness_Video",
        "Retargeting_Page_Viewers",
        "Prospecting_Interests_Tech",
    ]

    for date in dates:
        for campaign in campaigns:
            spend = np.random.uniform(50, 500)
            cpm = np.random.uniform(10, 25)
            impressions = int((spend / cpm) * 1000)
            ctr = np.random.uniform(0.008, 0.025)
            clicks = int(impressions * ctr)

            conv_rate = (
                np.random.uniform(0.02, 0.05) if "Retargeting" in campaign else np.random.uniform(0.005, 0.02)
            )
            conversions = int(clicks * conv_rate)
            roas = np.random.uniform(1.5, 4.0)
            revenue = spend * roas

            data.append(
                {
                    "date": date,
                    "campaign_name": campaign,
                    "ad_group": "All_Geos",
                    "ad_name": f"{campaign}_Creative_A",
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": round(spend, 2),
                    "conversions": conversions,
                    "revenue": round(revenue, 2),
                }
            )

    return pd.DataFrame(data)


def generate_mock_google_data(days: int = 30) -> pd.DataFrame:
    """Generate realistic mock data for Google Ads."""
    dates = pd.date_range(end=datetime.now(), periods=days)
    data = []

    campaigns = [
        "Search_Brand_protect",
        "Search_Generic_Best_Widgets",
        "Display_Remarketing",
        "YouTube_PreRoll_Awareness",
        "Performance_Max_All_Products",
    ]

    for date in dates:
        for campaign in campaigns:
            if "Brand" in campaign:
                spend = np.random.uniform(20, 100)
                ctr = np.random.uniform(0.10, 0.25)
                roas = np.random.uniform(5.0, 10.0)
            elif "YouTube" in campaign:
                spend = np.random.uniform(100, 300)
                ctr = np.random.uniform(0.001, 0.005)
                roas = np.random.uniform(0.8, 1.5)
            else:
                spend = np.random.uniform(50, 400)
                ctr = np.random.uniform(0.02, 0.06)
                roas = np.random.uniform(2.0, 5.0)

            cpm = np.random.uniform(5, 40)
            impressions = int((spend / cpm) * 1000)
            clicks = int(impressions * ctr)

            conv_rate = np.random.uniform(0.01, 0.04)
            conversions = int(clicks * conv_rate)
            revenue = spend * roas

            data.append(
                {
                    "date": date,
                    "campaign_name": campaign,
                    "ad_group": "Standard",
                    "ad_name": "Responsive_Search_Ad",
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": round(spend, 2),
                    "conversions": conversions,
                    "revenue": round(revenue, 2),
                }
            )

    return pd.DataFrame(data)
