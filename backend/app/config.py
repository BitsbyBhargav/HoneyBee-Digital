from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    mysql_host: str = '127.0.0.1'
    mysql_port: int = 3307
    mysql_database: str = 'honeybee'
    mysql_user: str = 'honeybee_app'
    mysql_password: str = Field(default='', repr=False)
    import_api_key: str = Field(default='', repr=False)
    cors_origins: list[str] = ['http://localhost:5173', 'http://127.0.0.1:5173']

    @property
    def database_url(self):
        # URL.create correctly handles @ and other special characters in passwords.
        return URL.create('mysql+pymysql', username=self.mysql_user,
                          password=self.mysql_password, host=self.mysql_host,
                          port=self.mysql_port, database=self.mysql_database,
                          query={'charset': 'utf8mb4'})


settings = Settings()
