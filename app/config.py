from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Sistema Academico API"
    app_version: str = "1.0.0"
    
    # IMPORTANTE: Esta línea debe estar indentada dentro de la clase
    database_url: str = "sqlite:///./academico.db"

    class Config:
        env_file = ".env"

# Instancia global
settings = Settings()