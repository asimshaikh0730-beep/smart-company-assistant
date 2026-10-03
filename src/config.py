"""All settings in one place. Change numbers here, not all over the code."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Paths
DATA_DIR = ROOT / "data"
POLICIES_DIR = DATA_DIR / "policies"
EMPLOYEES_FILE = DATA_DIR / "employees.json"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "company_policies"

# LLM (free Gemini tier). Change MODEL in .env if a model is not available.
MODEL = os.getenv("MODEL", "gemini-2.5-flash-lite")
MAX_RETRIES = 4  # retries for rate-limit (429) / temporary (503) errors

# Chunking
CHUNK_SIZE = 800     # max characters per chunk
CHUNK_OVERLAP = 100  # characters repeated between neighbouring chunks

# Retrieval
TOP_K = 4            # how many chunks to fetch
MAX_DISTANCE = 0.75  # cosine distance cut-off (lower = stricter). Tune using the eval.

# Guardrails
MAX_QUESTION_CHARS = 1000
