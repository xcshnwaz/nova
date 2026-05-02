"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NOVA AI — MongoDB Database Module
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from datetime import datetime, date
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from config import MONGO_URI, MONGO_DB_NAME

logger = logging.getLogger("NOVA-DB")


class Database:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client[MONGO_DB_NAME]
            self.users      = self.db["users"]
            self.messages   = self.db["messages"]
            self.banned     = self.db["banned"]
            self.broadcasts = self.db["broadcasts"]
            self._create_indexes()
            logger.info("✅ MongoDB connected!")
        except ConnectionFailure as e:
            logger.critical(f"❌ MongoDB connection failed: {e}")
            raise

    def _create_indexes(self):
        self.users.create_index("uid", unique=True)
        self.messages.create_index("uid")
        self.messages.create_index("timestamp")
        self.banned.create_index("uid", unique=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USER MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def add_user(self, uid: int, username: str, name: str):
        today = str(date.today())
        self.users.update_one(
            {"uid": uid},
            {"$setOnInsert": {
                "uid": uid,
                "username": username,
                "name": name,
                "plan": "free",
                "joined": today,
                "history": [],
                "daily_usage": 0,
                "last_usage_date": today,
                "message_times": [],
                "created_at": datetime.utcnow()
            },
             "$set": {"username": username, "name": name, "last_seen": datetime.utcnow()}},
            upsert=True
        )

    def get_user(self, uid: int) -> dict:
        return self.users.find_one({"uid": uid}, {"_id": 0}) or {}

    def get_all_users(self) -> list:
        return [u["uid"] for u in self.users.find({}, {"uid": 1, "_id": 0})]

    def get_all_users_detail(self) -> list:
        return list(self.users.find({}, {"_id": 0}).sort("created_at", DESCENDING).limit(50))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PLAN MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_plan(self, uid: int) -> str:
        user = self.users.find_one({"uid": uid}, {"plan": 1})
        return user.get("plan", "free") if user else "free"

    def set_plan(self, uid: int, plan: str):
        self.users.update_one(
            {"uid": uid},
            {"$set": {"plan": plan, "plan_updated": datetime.utcnow()}}
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DAILY USAGE TRACKING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_daily_usage(self, uid: int) -> int:
        user = self.users.find_one({"uid": uid}, {"daily_usage": 1, "last_usage_date": 1})
        if not user:
            return 0
        if user.get("last_usage_date") != str(date.today()):
            return 0
        return user.get("daily_usage", 0)

    def increment_usage(self, uid: int):
        today = str(date.today())
        user = self.users.find_one({"uid": uid}, {"last_usage_date": 1})
        if user and user.get("last_usage_date") != today:
            self.users.update_one({"uid": uid}, {"$set": {"daily_usage": 0, "last_usage_date": today}})
        self.users.update_one({"uid": uid}, {"$inc": {"daily_usage": 1}})

        # Global daily stats
        self.db["stats"].update_one(
            {"_id": "global"},
            {"$inc": {"messages_today": 1}, "$set": {"last_updated": datetime.utcnow()}},
            upsert=True
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHAT HISTORY (MEMORY)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_history(self, uid: int) -> list:
        user = self.users.find_one({"uid": uid}, {"history": 1})
        return user.get("history", []) if user else []

    def add_to_history(self, uid: int, role: str, content: str):
        self.users.update_one(
            {"uid": uid},
            {"$push": {"history": {
                "$each": [{"role": role, "content": content, "ts": datetime.utcnow()}],
                "$slice": -20  # Keep last 20 messages
            }}}
        )

    def clear_history(self, uid: int):
        self.users.update_one({"uid": uid}, {"$set": {"history": []}})

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SPAM PROTECTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def record_message(self, uid: int):
        now = time.time()
        # Keep only last 10 seconds of timestamps
        self.users.update_one(
            {"uid": uid},
            {"$push": {"message_times": {
                "$each": [now],
                "$slice": -20
            }}}
        )

    def is_spam(self, uid: int) -> bool:
        user = self.users.find_one({"uid": uid}, {"message_times": 1})
        if not user:
            return False
        now = time.time()
        recent = [t for t in user.get("message_times", []) if now - t < 10]
        return len(recent) > 8

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BAN SYSTEM
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def ban_user(self, uid: int):
        self.banned.update_one(
            {"uid": uid},
            {"$set": {"uid": uid, "banned_at": datetime.utcnow()}},
            upsert=True
        )

    def unban_user(self, uid: int):
        self.banned.delete_one({"uid": uid})

    def is_banned(self, uid: int) -> bool:
        return self.banned.find_one({"uid": uid}) is not None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATISTICS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def total_users(self) -> int:
        return self.users.count_documents({})

    def premium_users(self) -> int:
        return self.users.count_documents({"plan": "premium"})

    def banned_users_count(self) -> int:
        return self.banned.count_documents({})

    def messages_today(self) -> int:
        stats = self.db["stats"].find_one({"_id": "global"})
        return stats.get("messages_today", 0) if stats else 0

    def new_users_today(self) -> int:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.users.count_documents({"created_at": {"$gte": today_start}})


db = Database()
