import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

# Import Real Clients (Lazy import inside functions to avoid breaking if files missing during heavy dev)
from integrators.facebook_client import FacebookClient
from integrators.google_client import GoogleClient

def fetch_or_mock_facebook_data(days=30, use_mock=False):
    """
    Fetch Facebook data.
    If use_mock=True, return mock data immediately.
    If use_mock=False, try real API. If empty/error, return empty DataFrame (do NOT fallback).
    """
    if use_mock:
        print("🎭 Demo Mode: Generating Facebook Mock Data")
        return generate_mock_facebook_data(days)

    print("Attempting to fetch Real Facebook Data...")
    client = FacebookClient()
    if client.is_configured:
        df = client.get_campaign_insights(days=days)
        if df is not None and not df.empty:
            print("✅ Successfully fetched Real Facebook Data!")
            return df
        else:
            print("⚠️ Connected to Facebook, but no data found.")
            return pd.DataFrame() # Return empty to signify no real data
    else:
         print("❌ Facebook API not configured.")
         return pd.DataFrame()

def fetch_or_mock_google_data(days=30, use_mock=False):
    """
    Fetch Google data.
    If use_mock=True, return mock data immediately.
    If use_mock=False, try real API. If empty/error, return empty DataFrame (do NOT fallback).
    """
    if use_mock:
        print("🎭 Demo Mode: Generating Google Mock Data")
        return generate_mock_google_data(days)

    print("Attempting to fetch Real Google Ads Data...")
    client = GoogleClient()
    if client.is_configured:
        df = client.get_campaign_insights(days=days)
        if df is not None and not df.empty:
            print("✅ Successfully fetched Real Google Data!")
            return df
        else:
            print("⚠️ Connected to Google, but no data found.")
            return pd.DataFrame()
    else:
        print("❌ Google Ads API not configured.")
        return pd.DataFrame()

def generate_mock_facebook_data(days=30):
    """Generate realistic mock data for Facebook Ads"""
    dates = pd.date_range(end=datetime.now(), periods=days)
    data = []
    
    campaigns = [
        "Retargeting_Cart_Abandoners",
        "Prospecting_Lookalike_1%",
        "Brand_Awareness_Video",
        "Retargeting_Page_Viewers",
        "Prospecting_Interests_Tech"
    ]
    
    for date in dates:
        for campaign in campaigns:
            # Randomize metrics with realistic correlations
            spend = np.random.uniform(50, 500)
            cpm = np.random.uniform(10, 25)
            impressions = int((spend / cpm) * 1000)
            ctr = np.random.uniform(0.008, 0.025)
            clicks = int(impressions * ctr)
            cpc = spend / clicks if clicks > 0 else 0
            
            # Conversion rate higher for retargeting
            if "Retargeting" in campaign:
                conv_rate = np.random.uniform(0.02, 0.05)
            else:
                conv_rate = np.random.uniform(0.005, 0.02)
                
            conversions = int(clicks * conv_rate)
            # CPA and ROAS
            cpa = spend / conversions if conversions > 0 else 0
            roas = np.random.uniform(1.5, 4.0)
            revenue = spend * roas
            
            data.append({
                'date': date,
                'campaign_name': campaign,
                'ad_group': 'All_Geos',
                'ad_name': f"{campaign}_Creative_A",
                'impressions': impressions,
                'clicks': clicks,
                'spend': round(spend, 2),
                'conversions': conversions,
                'revenue': round(revenue, 2)
            })
            
    return pd.DataFrame(data)

def generate_mock_google_data(days=30):
    """Generate realistic mock data for Google Ads"""
    dates = pd.date_range(end=datetime.now(), periods=days)
    data = []
    
    campaigns = [
        "Search_Brand_protect",
        "Search_Generic_Best_Widgets",
        "Display_Remarketing",
        "YouTube_PreRoll_Awareness",
        "Performance_Max_All_Products"
    ]
    
    for date in dates:
        for campaign in campaigns:
            if "Brand" in campaign:
                spend = np.random.uniform(20, 100)
                ctr = np.random.uniform(0.10, 0.25) # Brand CTR is high
                roas = np.random.uniform(5.0, 10.0)
            elif "YouTube" in campaign:
                spend = np.random.uniform(100, 300)
                ctr = np.random.uniform(0.001, 0.005) # Video CTR low
                roas = np.random.uniform(0.8, 1.5)
            else:
                spend = np.random.uniform(50, 400)
                ctr = np.random.uniform(0.02, 0.06)
                roas = np.random.uniform(2.0, 5.0)

            cpm = np.random.uniform(5, 40)
            impressions = int((spend / cpm) * 1000)
            clicks = int(impressions * ctr)
            
            # Conversions
            conv_rate = np.random.uniform(0.01, 0.04)
            conversions = int(clicks * conv_rate)
            revenue = spend * roas
            
            data.append({
                'date': date,
                'campaign_name': campaign,
                'ad_group': 'Standard',
                'ad_name': 'Responsive_Search_Ad',
                'impressions': impressions,
                'clicks': clicks,
                'spend': round(spend, 2),
                'conversions': conversions,
                'revenue': round(revenue, 2)
            })
            
    return pd.DataFrame(data)
