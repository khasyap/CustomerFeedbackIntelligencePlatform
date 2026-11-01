import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./customer_feedback.db")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    RANDOM_SEED: int = int(os.getenv("RANDOM_SEED", 20261022))
    APP_ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "feedback-intelligence-secret-key-2026")
    CORS_ORIGINS: list[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,*").split(",")
    ]
    DATA_DIR: str = os.getenv("DATA_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
    
    # Classification thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.75
    LOW_CONFIDENCE_THRESHOLD: float = 0.45
    
    # Priority engine weights
    WEIGHT_NEGATIVE_RATE: float = 0.35
    WEIGHT_VOLUME: float = 0.25
    WEIGHT_SEVERITY: float = 0.20
    WEIGHT_GROWTH_RATE: float = 0.10
    WEIGHT_CUSTOMER_IMPACT: float = 0.10

settings = Settings()
