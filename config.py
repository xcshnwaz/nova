import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8538070031:AAGU152MzUel5GQ2Qzo985lHuPIxDFnNAaU")

ADMIN_IDS_RAW = os.environ.get("ADMIN_IDS", "8508081184")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBC7pUqYHJB4TFPkXMPu-B-OpkAfFSve5Y")

MONGO_URI     = os.environ.get("MONGO_URI", "mongodb+srv://shnwaz38:shnwaz38@cluster0.itsfvvz.mongodb.net/?appName=Cluster0")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "nova_ai_bot")

RENDER_URL   = os.environ.get("https://nova-mwgl.onrender.com", "")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/webhook")
PORT         = int(os.environ.get("PORT", 8443))

FREE_DAILY_LIMIT    = int(os.environ.get("FREE_DAILY_LIMIT", "30"))
PREMIUM_DAILY_LIMIT = int(os.environ.get("PREMIUM_DAILY_LIMIT", "9999"))

BOT_NAME       = "NOVA AI"
BOT_VERSION    = "3.0"
ADMIN_USERNAME = os.environ.get("cylxowner", "your_admin_username")
