from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Corvus Integrator Project Clustering Service"
    API_V1_STR: str = "/api/v1"
    PORT: int = 3002

    # Google API
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Base de Datos
    CHROMA_DB_PATH: str = "./chroma_data"
    POSTGRES_DB_URL: str = "postgresql://postgres:postgres@localhost:5433/corvus_clustering_integrator_db"
    
    # Microservicios
    AUTH_SERVICE_URL: str = "http://localhost:3001"
    
    # Modelos IA
    MODELS_DIR: str = "./app/models"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
