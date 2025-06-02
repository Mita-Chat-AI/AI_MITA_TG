from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

from pathlib import Path

class Settings(BaseSettings):
    bot_token: SecretStr
    owner_id: SecretStr
    voice_api: SecretStr
    socks_proxy: SecretStr
    model_ollama: SecretStr
    ollama_api: SecretStr
    max_ollama_chars: SecretStr
    memory_dir: SecretStr
    asr_api: SecretStr
    channel_id: SecretStr
    voice_channel: SecretStr
    log_channel_id: SecretStr
    mongo_db: SecretStr
    mongo_name: SecretStr
    start_video_url: SecretStr
    voice_channel_username: SecretStr
    help_pic_url: SecretStr
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / '.env', env_file_encoding='UTF-8'
    )

config = Settings()
