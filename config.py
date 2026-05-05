from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_name: str
    db_username: str
    db_password: str
    jwt_key: str
    jwt_issuer: str = "iJewellery"
    jwt_audience: str = "iJewellery"
    business_db_1: str = "iJewellery"
    business_db_2: str = "iJewellery_radhe"

    @property
    def business_databases(self) -> dict:
        return {1: self.business_db_1, 2: self.business_db_2}

    class Config:
        env_file = ".env"


settings = Settings()
