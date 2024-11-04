import os

class Config:
    POSTGRES_URI = os.getenv("POSTGRES_URI", "")
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "")
