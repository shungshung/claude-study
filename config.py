import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 4096
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
