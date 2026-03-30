from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    database_url: str = "sqlite:///./db.sqlite3"

    thesportsdb_api_key: str = "123"
    thesportsdb_base_url: str = "https://www.thesportsdb.com/api/v1/json"

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    timezone: str = "Europe/Kyiv"
    scheduler_enabled: bool = False
    default_stake: float = 100.0

    prediction_window_days: int = 3
    prediction_limit: int = 10
    min_predictions_to_send: int = 3
    min_confidence: int = 54
    min_data_quality: float = 20.0

    btc_symbol: str = "BTCUSDT"
    btc_quote_asset: str = "USDT"
    bot_poll_interval_sec: int = 8
    bot_loop_sleep_sec: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
