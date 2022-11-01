from pydantic import BaseSettings
import datetime as dt


class PostgresEnv(BaseSettings):
    """
    Переменные окружения.
    """
    USER: str
    PASSWORD: str
    DB: str
    HOST: str
    PORT: str

    class Config:
        env_prefix = 'POSTGRES_'
        env_file = '.env'
        env_file_encoding = 'utf-8'


class JWTEnv(BaseSettings):
    JWT_SECRET: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
    

postgres_env = PostgresEnv()
jwt_env = JWTEnv()
JWT_AT_LIFETIME = dt.timedelta(minutes=5)
JWT_RT_LIFETIME = dt.timedelta(days=7)
JWT_AT_TYPE = 'bearer'
