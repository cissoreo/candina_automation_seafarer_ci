import os
from pathlib import Path
import sys

from dotenv import load_dotenv



def load_config():
    if getattr(sys, "frozen", False):
        BASE_DIR = Path(sys.executable).parent
    else:
        BASE_DIR = Path(__file__).parent
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return None
    load_dotenv(env_path)
    return {
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", "").strip(),
        "anthropic_model": os.getenv(
            "ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"
        ).strip(),
        "supabase_url": os.getenv("SUPABASE_URL", "").strip(),
        "supabase_key": os.getenv("SUPABASE_KEY", "").strip(),
    }