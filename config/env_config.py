from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import os

load_dotenv()

class EnvConfig(BaseModel):
    DB_USERNAME: str = Field(..., description="Mongo DB Username string")
    DB_PASSWORD: str = Field(..., description="Mongo DB Password string")
    DB_NAME: str = Field(..., description="Mongo DB Name string")
    JWT_SECRET_KEY: str = Field(..., description="JWT Secret Key string")
    GENAI_API_KEY: str = Field(..., description="Google Gemini API Key")

def get_env_config() -> EnvConfig:
    try:
        config = EnvConfig(**os.environ)
        return config
    except ValidationError as error:
        print("Environment validation failed!")
        print(error)
        exit(1)
