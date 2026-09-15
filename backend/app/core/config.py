"""
Application configuration.

Centralizes all environment-driven settings so the rest of the codebase
never reads `os.environ` directly. Import `settings` wherever a config
value is needed.
"""
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "Ad Performance Intelligence Engine"
    environment: str = "development"
    log_level: str = "INFO"

    # --- Auth ---
    # In production this MUST be provided via the SECRET_KEY env var.
    # The random fallback keeps local/dev usage working out of the box
    # while making it obvious (a new key every restart) that it hasn't
    # been configured for anything persistent.
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- Database ---
    database_url: str = "sqlite:///./ad_engine.db"

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000"]

    # --- Default admin (dev convenience) ---
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "admin"

    # --- Optional AI-enhanced insights (skipped entirely if unset) ---
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # --- Facebook / Meta Marketing API ---
    fb_access_token: str | None = None
    fb_ad_account_id: str | None = None
    fb_app_id: str | None = None
    fb_app_secret: str | None = None

    # --- Google Ads API ---
    google_ads_developer_token: str | None = None
    google_ads_client_id: str | None = None
    google_ads_client_secret: str | None = None
    google_ads_refresh_token: str | None = None
    google_ads_login_customer_id: str | None = None
    google_ads_customer_id: str | None = None


settings = Settings()
