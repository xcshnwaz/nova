"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NOVA AI — Configuration File
  ⚠️  Yahan apni values dalo!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os

# ── Telegram Bot Token ─────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ── Admin Telegram User IDs ────────────────────────────────
ADMIN_IDS_RAW = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

# ── Google Gemini API Key ──────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# ── MongoDB Connection ─────────────────────────────────────
MONGO_URI     = os.environ.get("MONGO_URI", "YOUR_MONGODB_URI_HERE")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "nova_ai_bot")

# ── Render / Webhook Settings ──────────────────────────────
RENDER_URL   = os.environ.get("RENDER_URL", "")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/webhook")
PORT         = int(os.environ.get("PORT", 8443))

# ── Plans ──────────────────────────────────────────────────
FREE_DAILY_LIMIT    = int(os.environ.get("FREE_DAILY_LIMIT", "30"))
PREMIUM_DAILY_LIMIT = int(os.environ.get("PREMIUM_DAILY_LIMIT", "9999"))

# ── Bot Meta ───────────────────────────────────────────────
BOT_NAME       = "NOVA AI"
BOT_VERSION    = "3.0"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "your_admin_username")
