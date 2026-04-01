# ============================================================
#  config.py — Database & App Configuration
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# ── MySQL Configuration ───────────────────────────────────
DB_CONFIG = {
    'host':     os.getenv('DB_HOST',     'localhost'),
    'port':     int(os.getenv('DB_PORT', 3306)),
    'user':     os.getenv('DB_USER',     'root'),
    'password': os.getenv('DB_PASSWORD', '015Rohit@'),
    'database': os.getenv('DB_NAME',     'shopmind_db'),
}

# ── NLP Configuration ─────────────────────────────────────
USE_BERT       = False   # Set True to use Sentence-BERT (slower but more accurate)
CONFIDENCE_THRESHOLD = 0.51  # Minimum similarity score to accept an intent

# ── App Settings ──────────────────────────────────────────
MAX_CHAT_LOG   = 1000    # Keep last N chat logs in DB
