"""Configuration and environment setup."""

import os
import logging
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv


def setup_logging() -> logging.Logger:
    """Configure logging to file and console."""
    Path(".logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('.logs/app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def load_environment() -> Tuple[str, str]:
    """Load and validate environment variables."""
    load_dotenv()
    
    langsmith_key = os.getenv("LANGSMITH_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if not langsmith_key:
        raise EnvironmentError("LANGSMITH_API_KEY not set in environment. Add it to your .env file.")
    if not google_key:
        raise EnvironmentError("GOOGLE_API_KEY not set in environment. Add it to your .env file.")
    
    print("✓ Environment variables loaded successfully")
    return langsmith_key, google_key


logger = setup_logging()
LANGSMITH_API_KEY, GOOGLE_API_KEY = load_environment()
