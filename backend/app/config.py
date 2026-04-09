from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/app -> backend
PROJECT_DIR = BASE_DIR.parent  # ir_proj
DATA_DIR = PROJECT_DIR / "data"
CACHE_DIR = BASE_DIR / "app" / "data"

DOCS_FILE = DATA_DIR / "cran.all.1400.xml"
QUERY_FILE = DATA_DIR / "cran.qry.xml"
QREL_FILE = DATA_DIR / "cranqrel.txt"
INDEX_CACHE = CACHE_DIR / "index.pkl"
