"""Application configuration with environment variable support."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "GreenForge AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./greenforge.db"

    # IBM Granite / watsonx.ai
    IBM_API_KEY: Optional[str] = None
    IBM_PROJECT_ID: Optional[str] = None
    IBM_SERVICE_URL: str = "https://us-south.ml.cloud.ibm.com"
    GRANITE_MODEL_ID: str = "ibm/granite-13b-instruct-v2"

    # Benchmark settings
    BENCHMARK_TIMEOUT: int = 30
    BENCHMARK_RUNS: int = 5
    MAX_CODE_SIZE_KB: int = 512
    MAX_OUTPUT_SIZE_KB: int = 256

    # Sustainability defaults (configurable)
    DEFAULT_CPU_TDP_WATTS: float = 95.0
    DEFAULT_GPU_TDP_WATTS: float = 250.0
    DEFAULT_GRID_CARBON_INTENSITY: float = 475.0  # gCO2/kWh world average
    DEFAULT_PUE: float = 1.5
    DEFAULT_CPU_UTILIZATION: float = 0.5

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
