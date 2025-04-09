# backend/utils/paths.py

from pathlib import Path
from os.path import join as join_path

# This assumes `backend/` is your top-level package
ROOT_DIR = Path(__file__).resolve()


def find_dotenv(start_path: Path = ROOT_DIR) -> Path:
    """Find the .env file in the directory tree starting from start_path."""
    for parent in [start_path] + list(start_path.parents):
        potential = parent / '.env'
        if potential.exists():
            return parent
    raise FileNotFoundError(".env file not found")

ENV_PATH = join_path(find_dotenv(), ".env")
