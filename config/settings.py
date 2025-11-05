import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
OUTPUT_DIR = DATA_DIR / "output"
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "production.db"

# Beamteq log parser settings
LOG_ENCODING = "utf-8"
