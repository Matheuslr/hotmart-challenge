import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self) -> None:
        self.url = os.getenv("EXTERNAL_API_URL")
        self.oauth_key = os.getenv("OAUTH_GITHUB_KEY")

settings = Settings()