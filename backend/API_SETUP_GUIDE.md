# Ad Engine - API Setup Guide

## 1. Facebook Ads (Meta Marketing API)

### Prerequisites
- A Facebook Business Manager account.
- An active Ad Account.

### Steps
1.  **Create an App**:
    - Go to [developers.facebook.com](https://developers.facebook.com/).
    - Click **My Apps** -> **Create App**.
    - Select **"Other"** -> **"Business"**.
    - Usage: **"Marketing API"**.

2.  **Get Credentials**:
    - **App ID & Secret**: Go to **Settings** -> **Basic** in your App Dashboard.
    - **Access Token**: 
        - Go to **Marketing API** -> **Tools** (in sidebar).
        - Select your permissions (`ads_read`) and your Ad Account.
        - Click **Get Token**.
    - **Ad Account ID**: 
        - Go to [Ads Manager](https://adsmanager.facebook.com/).
        - Copy the ID from the URL (`act=12345...`) or the dropdown.

3.  **Update `.env`**:
    ```ini
    FB_APP_ID=...
    FB_APP_SECRET=...
    FB_ACCESS_TOKEN=...
    FB_AD_ACCOUNT_ID=act_...
    ```

---

## 2. Google Ads API

### Prerequisites
- A Google Ads Manager Account (MCC).

### Steps
1.  **Developer Token**:
    - Log in to your Google Ads Manager Account.
    - Go to **Tools & Settings** -> **Setup** -> **API Center**.
    - Copy your **Developer Token**. (Use "Test Access" level for development).

2.  **OAuth Credentials (Cloud Console)**:
    - Go to [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new Project.
    - Search for **"Google Ads API"** and **Enable** it.
    - Go to **Credentials** -> **Create Credentials** -> **OAuth Client ID** (Web Application).
    - Set Redirect URI to `https://developers.google.com/oauthplayground` (easiest for getting refresh token).
    - Copy **Client ID** and **Client Secret**.

3.  **Refresh Token**:
    - Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground).
    - Select **Google Ads API** (`https://www.googleapis.com/auth/adwords`).
    - Click **Authorize API** -> Login -> Allow.
    - Click **Exchange authorization code for tokens**.
    - Copy the **Refresh Token**.

4.  **Customer ID**:
    - This is the XXX-XXX-XXXX number in the top right of your Google Ads account (main login customer or sub-account).

5.  **Update `.env`**:
    ```ini
    GOOGLE_ADS_DEVELOPER_TOKEN=...
    GOOGLE_ADS_CLIENT_ID=...
    GOOGLE_ADS_CLIENT_SECRET=...
    GOOGLE_ADS_REFRESH_TOKEN=...
    GOOGLE_ADS_LOGIN_CUSTOMER_ID=... (Your MCC ID)
    GOOGLE_ADS_CUSTOMER_ID=... (The account with the data)
    ```
