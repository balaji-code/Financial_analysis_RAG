from pathlib import Path

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

COMPANY = "ITC"

YEARS = [2021, 2022, 2023, 2024, 2025]

MD_A_SECTION = "MD&A"

EMBEDDING_MODEL = "text-embedding-3-large"