from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BharatData"
    environment: str = "development"
    database_url: str = "sqlite:///./bharatdata.db"
    data_gov_in_api_key: str = ""
    data_gov_in_base_url: str = "https://api.data.gov.in/resource"
    apify_token: str = ""
    apify_actor_id: str = "themineworks~india-data-gov-scraper"
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 20
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

settings = Settings()
