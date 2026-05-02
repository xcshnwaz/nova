"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NOVA AI — Premium Hindi Telegram Bot v3.0
  MongoDB + Render Webhook + Gemini AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging
import random
import asyncio
import os
from datetime import datetime
from functools import wraps

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode, ChatAction

from config import (
    BOT_TOKEN, ADMIN_IDS, RENDER_URL,
    WEBHOOK_PATH, PORT, FREE_DAILY_LIMIT,
    PREMIUM_DAILY_LIMIT, ADMIN_USERNAME, BOT_VERSION
)
from stickers import STICKER_IDS
from database import db
from ai_engine import AIEngine

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("nova_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NOVA-BOT")
ai = AIEngine()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DECORATORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("🚫 *Sirf Admin kar sakta hai ye!*", parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, ctx)
    return wrapper


def spam_check(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if db.is_banned(uid):
            await update.message.reply_text("🔴 *Aap ban hain. Admin se contact karein.*", parse_mode=ParseMode.MARKDOWN)
            return
        if db.is_spam(uid):
            await update.message.reply_text("⚠️ *Itni jaldi mat karo! Thoda slow karo.*", parse_mode=ParseMode.MARKDOWN)
            return
        db.record_message(uid)
        return await func(update, ctx)
    return wrapper


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /start
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    uid    = user.id
    name   = user.first_name or "Dost"

    db.add_user(uid, user.username or "", name)
    plan   = db.get_plan(uid)
    badge  = "👑 Premium" if plan == "premium" else "🆓 Free"

    await update.message.reply_sticker(random.choice(STICKER_IDS))

    text = f"""
╔══════════════════════════╗
║  🤖 *NOVA AI में स्वागत है!*  ║
╚══════════════════════════╝

नमस्ते *{name}* जी! 🙏

मैं हूँ *NOVA* — आपका AI दोस्त!
Hindi में बात करें, मैं समझूँगा! 😊

━━━━━━━━━━━━━━━━━━━━
🆔 ID: `{uid}`
💎 Plan: {badge}
🤖 Version: v{BOT_VERSION}
━━━━━━━━━━━━━━━━━━━━

⚡ *क्या कर सकता हूँ:*
✅ Hindi smart conversation
✅ Documents & files analyze
✅ सवालों के जवाब
✅ Stickers भेजना
✅ Deep conversation mode
"""
    kb = [
        [InlineKeyboardButton("💬 Chat शुरू", callback_data="chat"),
         InlineKeyboardButton("📋 Commands", callback_data="help")],
        [InlineKeyboardButton("👑 Premium लें", callback_data="premium"),
         InlineKeyboardButton("📊 मेरा Profile", callback_data="myprofile")],
        [InlineKeyboardButton("📞 Support", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(kb)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 *NOVA AI — Command List*
━━━━━━━━━━━━━━━━━━━━━━━━

👤 *User Commands:*
/start — Bot शुरू करें
/help — Command list
/profile — अपनी profile
/reset — Memory reset
/sticker — Random sticker
/plan — Plan details
/deep — Deep mode ON
/normal — Normal mode

━━━━━━━━━━━━━━━━━━━━━━━━
🔐 *Admin Commands:*
/broadcast `<msg>` — Sabko bhejo
/ban `<id>` — Ban karo
/unban `<id>` — Unban karo
/addpremium `<id>` — Premium do
/removepremium `<id>` — Premium hato
/stats — Bot statistics
/userlist — User list
━━━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /profile
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def profile_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user  = update.effective_user
    uid   = user.id
    data  = db.get_user(uid)
    plan  = db.get_plan(uid)
    used  = db.get_daily_usage(uid)
    limit = PREMIUM_DAILY_LIMIT if plan == "premium" else FREE_DAILY_LIMIT
    badge = "👑 Premium" if plan == "premium" else "🆓 Free"
    bar   = "█" * min(10, int((used / max(limit,1)) * 10)) + "░" * (10 - min(10, int((used / max(limit,1)) * 10)))

    text = f"""
╔══════════════════════╗
║   👤 *आपकी Profile*   ║
╚══════════════════════╝

🏷️ *नाम:* {user.first_name}
🆔 *ID:* `{uid}`
👤 *Username:* @{user.username or 'N/A'}
💎 *Plan:* {badge}
📅 *Joined:* {data.get('joined', 'N/A')}

━━━━━━━━━━━━━━━━━
📊 *आज का Usage:*
`[{bar}]` {used}/{limit}
━━━━━━━━━━━━━━━━━
"""
    kb = [[InlineKeyboardButton("👑 Premium Upgrade", callback_data="premium")]]
    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(kb)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /sticker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def sticker_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_sticker(random.choice(STICKER_IDS))
    await update.message.reply_text("😄 *Ye lo ek sticker!*", parse_mode=ParseMode.MARKDOWN)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /reset  /deep  /normal  /plan
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def reset_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db.clear_history(update.effective_user.id)
    await update.message.reply_sticker(random.choice(STICKER_IDS))
    await update.message.reply_text("🔄 *Memory reset ho gayi! Fresh start karo!* 😊", parse_mode=ParseMode.MARKDOWN)

async def deep_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["deep_mode"] = True
    await update.message.reply_text("🧠 *Deep Mode ON!*\nAb detailed replies milenge. /normal se wapas jao.", parse_mode=ParseMode.MARKDOWN)

async def normal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["deep_mode"] = False
    await update.message.reply_text("💬 *Normal Mode ON!* Fast & short replies active.", parse_mode=ParseMode.MARKDOWN)

async def plan_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    plan  = db.get_plan(uid)
    badge = "✅ आप *Premium* पर हैं!" if plan == "premium" else "📌 आप *Free Plan* पर हैं"
    text = f"""
╔═══════════════════════╗
║  💎 *Subscription Plans* ║
╚═══════════════════════╝

{badge}

━━━━━━━━━━━━━━━━━━━━
🆓 *Free Plan:*
• {FREE_DAILY_LIMIT} messages/day
• Basic AI chat
• Stickers support

👑 *Premium Plan:*
• {PREMIUM_DAILY_LIMIT} messages/day
• Advanced AI responses ⚡
• Deep conversation mode 🧠
• File analysis 📁
• Priority speed
• 24/7 VIP support

━━━━━━━━━━━━━━━━━━━━
💰 Admin se contact karein!
"""
    kb = [[InlineKeyboardButton("📞 Admin Contact", url=f"https://t.me/{ADMIN_USERNAME}")]]
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CHAT HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@spam_check
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    user = update.effective_user
    uid  = user.id

    # Ensure user exists
    db.add_user(uid, user.username or "", user.first_name or "User")

    # Route to file handlers
    if msg.document:
        await handle_document(update, ctx); return
    if msg.photo:
        await handle_photo(update, ctx); return

    text = (msg.text or "").strip()
    if not text:
        return

    # Daily limit check
    plan  = db.get_plan(uid)
    limit = PREMIUM_DAILY_LIMIT if plan == "premium" else FREE_DAILY_LIMIT
    used  = db.get_daily_usage(uid)

    if used >= limit:
        kb = [[InlineKeyboardButton("👑 Premium — Unlimited Chat!", callback_data="premium")]]
        await msg.reply_text(
            f"⚠️ *Daily limit ({limit} messages) khatam!*\n\n👑 Premium lo aur unlimited chat karo!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # Typing indicator
    await ctx.bot.send_chat_action(chat_id=uid, action=ChatAction.TYPING)

    history   = db.get_history(uid)
    deep_mode = ctx.user_data.get("deep_mode", False)

    try:
        reply = await ai.chat(text, history, deep_mode=deep_mode)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        reply = "Oops! Thodi problem aayi. Phir se try karo! 🙏"

    db.add_to_history(uid, "user", text)
    db.add_to_history(uid, "assistant", reply)
    db.increment_usage(uid)

    # 10% chance of random sticker
    if random.random() < 0.10:
        await msg.reply_sticker(random.choice(STICKER_IDS))

    await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    doc  = msg.document
    name = doc.file_name or "document"
    size = (doc.file_size or 0) / 1024

    await ctx.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.TYPING)

    if doc.file_size > 5 * 1024 * 1024:
        await msg.reply_text("⚠️ *File bahut badi hai! Max 5MB allowed.*", parse_mode=ParseMode.MARKDOWN)
        return

    status = await msg.reply_text(f"📄 *{name}* mil gayi!\n⏳ Process ho rahi hai...", parse_mode=ParseMode.MARKDOWN)

    try:
        file      = await ctx.bot.get_file(doc.file_id)
        file_path = f"/tmp/{name}"
        await file.download_to_drive(file_path)

        content = ""
        if name.endswith(".txt"):
            with open(file_path, "r", errors="ignore") as f:
                content = f.read()[:3000]
        elif name.endswith(".json"):
            import json
            with open(file_path, "r") as f:
                content = json.dumps(json.load(f), indent=2, ensure_ascii=False)[:3000]
        elif name.endswith(".py") or name.endswith(".js") or name.endswith(".html"):
            with open(file_path, "r", errors="ignore") as f:
                content = f.read()[:3000]
        else:
            content = f"File '{name}' receive hua. Format directly readable nahi hai."

        summary = await ai.summarize_file(name, content) if content else f"📄 `{name}` mili, lekin content read nahi ho saka."
        await status.edit_text(summary, parse_mode=ParseMode.MARKDOWN)
        os.remove(file_path)
    except Exception as e:
        logger.error(f"File error: {e}")
        await status.edit_text("❌ *File process karne mein error.* Dobara try karo.", parse_mode=ParseMode.MARKDOWN)


async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    await update.message.reply_text(
        "🖼️ *Photo mili!*\n\nPhoto ke baare mein kuch puchna ho toh batao! 😊",
        parse_mode=ParseMode.MARKDOWN
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADMIN COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@admin_only
async def broadcast_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("📢 Usage: `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
        return
    bcast = " ".join(ctx.args)
    users = db.get_all_users()
    sent  = failed = 0

    status = await update.message.reply_text(f"📤 Broadcasting to {len(users)} users...")
    for uid in users:
        try:
            await ctx.bot.send_message(chat_id=uid, text=f"📢 *NOVA AI — Broadcast*\n\n{bcast}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
            await asyncio.sleep(0.04)
        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ *Broadcast Complete!*\n📤 Sent: {sent}\n❌ Failed: {failed}",
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def ban_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/ban <user_id>`", parse_mode=ParseMode.MARKDOWN); return
    try:
        target = int(ctx.args[0])
        db.ban_user(target)
        await update.message.reply_text(f"🔴 User `{target}` ban ho gaya!", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ Valid ID dalo.")

@admin_only
async def unban_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/unban <user_id>`", parse_mode=ParseMode.MARKDOWN); return
    try:
        target = int(ctx.args[0])
        db.unban_user(target)
        await update.message.reply_text(f"✅ User `{target}` unban ho gaya!", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ Valid ID dalo.")

@admin_only
async def addpremium_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/addpremium <user_id>`", parse_mode=ParseMode.MARKDOWN); return
    try:
        target = int(ctx.args[0])
        db.set_plan(target, "premium")
        await update.message.reply_text(f"👑 User `{target}` ko Premium diya!", parse_mode=ParseMode.MARKDOWN)
        try:
            await ctx.bot.send_message(
                chat_id=target,
                text="🎉 *Congratulations!* Aapko *Premium Plan* mil gaya!\nUnlimited chat enjoy karo! 🚀",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Valid ID dalo.")

@admin_only
async def removepremium_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/removepremium <user_id>`", parse_mode=ParseMode.MARKDOWN); return
    try:
        target = int(ctx.args[0])
        db.set_plan(target, "free")
        await update.message.reply_text(f"🔓 User `{target}` ka Premium remove kiya.", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ Valid ID dalo.")

@admin_only
async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = f"""
📊 *NOVA AI — Statistics*
━━━━━━━━━━━━━━━━━━━━━━━
👥 Total Users:    *{db.total_users()}*
👑 Premium Users:  *{db.premium_users()}*
🔴 Banned Users:   *{db.banned_users_count()}*
💬 Messages Today: *{db.messages_today()}*
🆕 New Today:      *{db.new_users_today()}*
🎭 Total Stickers: *{len(STICKER_IDS)}*
━━━━━━━━━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@admin_only
async def userlist_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users_detail()
    if not users:
        await update.message.reply_text("No users yet."); return
    text = "👥 *Users (latest 20):*\n━━━━━━━━━━━━━━━\n"
    for u in users[:20]:
        icon = "👑" if u.get("plan") == "premium" else "🆓"
        text += f"{icon} `{u['uid']}` — {u.get('name','N/A')} (@{u.get('username','N/A')})\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CALLBACK QUERY HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    uid  = update.effective_user.id
    await q.answer()
    d = q.data

    if d == "help":
        await q.message.reply_text("📋 /help type karo command list ke liye!")
    elif d == "chat":
        await q.message.reply_text("💬 *Baat karo!* Koi bhi message type karo! 😊", parse_mode=ParseMode.MARKDOWN)
    elif d == "myprofile":
        used  = db.get_daily_usage(uid)
        plan  = db.get_plan(uid)
        limit = PREMIUM_DAILY_LIMIT if plan == "premium" else FREE_DAILY_LIMIT
        bar   = "█" * min(10, int((used/max(limit,1))*10)) + "░"*(10-min(10,int((used/max(limit,1))*10)))
        await q.message.reply_text(
            f"📊 *Quick Stats:*\n`[{bar}]` {used}/{limit} messages today\n💎 Plan: {'👑 Premium' if plan=='premium' else '🆓 Free'}",
            parse_mode=ParseMode.MARKDOWN
        )
    elif d == "premium":
        plan = db.get_plan(uid)
        if plan == "premium":
            await q.message.reply_text("✅ *Aap already Premium hain!*", parse_mode=ParseMode.MARKDOWN)
        else:
            kb = [[InlineKeyboardButton("📞 Admin Contact", url=f"https://t.me/{ADMIN_USERNAME}")]]
            await q.message.reply_text(
                f"👑 *Premium Plan:*\n\n• Unlimited messages\n• Deep AI mode\n• File analysis\n• Priority speed\n\nAdmin se contact karein!",
                parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb)
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW MEMBER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def new_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot: continue
        await update.message.reply_sticker(random.choice(STICKER_IDS))
        await update.message.reply_text(
            f"🎉 *{member.first_name} ji, NOVA AI group mein swagat hai!*\n/start karke mujhse baat karo! 😊",
            parse_mode=ParseMode.MARKDOWN
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ERROR HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {ctx.error}", exc_info=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REGISTER ALL HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def register_handlers(app: Application):
    # User commands
    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    help_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("sticker", sticker_cmd))
    app.add_handler(CommandHandler("reset",   reset_cmd))
    app.add_handler(CommandHandler("deep",    deep_cmd))
    app.add_handler(CommandHandler("normal",  normal_cmd))
    app.add_handler(CommandHandler("plan",    plan_cmd))

    # Admin commands
    app.add_handler(CommandHandler("broadcast",     broadcast_cmd))
    app.add_handler(CommandHandler("ban",            ban_cmd))
    app.add_handler(CommandHandler("unban",          unban_cmd))
    app.add_handler(CommandHandler("addpremium",     addpremium_cmd))
    app.add_handler(CommandHandler("removepremium",  removepremium_cmd))
    app.add_handler(CommandHandler("stats",          stats_cmd))
    app.add_handler(CommandHandler("userlist",       userlist_cmd))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,  handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL,              handle_message))
    app.add_handler(MessageHandler(filters.PHOTO,                     handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Errors
    app.add_error_handler(error_handler)

    return app


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN — Webhook (Render) or Polling (Local)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    logger.info("🚀 NOVA AI v3.0 starting...")
    app = Application.builder().token(BOT_TOKEN).build()
    app = register_handlers(app)

    if RENDER_URL:
        # ── Webhook mode (Render production) ──────────────
        webhook_url = f"{RENDER_URL}{WEBHOOK_PATH}"
        logger.info(f"🌐 Webhook mode: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=WEBHOOK_PATH,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # ── Polling mode (local development) ──────────────
        logger.info("🔄 Polling mode (local)")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
