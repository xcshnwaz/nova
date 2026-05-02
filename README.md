# 🤖 NOVA AI — Premium Hindi Telegram Bot v3.0
### MongoDB + Render.com + Google Gemini AI

---

## 📁 File Structure
```
nova_ai_bot/
├── bot.py            ← Main bot (all commands + webhook)
├── ai_engine.py      ← Gemini AI (Hindi responses)
├── database.py       ← MongoDB database module
├── config.py         ← Settings (reads from env vars)
├── stickers.py       ← 662 sticker IDs (6 packs)
├── requirements.txt  ← Python dependencies
├── Procfile          ← Render.com start command
├── runtime.txt       ← Python version for Render
├── render.yaml       ← Render deploy configuration
├── .env.example      ← Environment variables template
└── README.md         ← Yeh file
```

---

## 🗃️ Step 1 — MongoDB Atlas Setup (Free)

1. https://mongodb.com/atlas pe jaao
2. **"Try Free"** → Account banao
3. **Free Cluster (M0)** select karo
4. Region: **Mumbai (ap-south-1)** choose karo
5. Cluster naam: `nova-bot`
6. **Create** dabao

### Connection String lena:
1. Left menu → **Database Access** → **Add New Database User**
   - Username: `novabot`
   - Password: koi strong password (copy kar lo!)
   - Role: **Atlas Admin** → **Add User**

2. Left menu → **Network Access** → **Add IP Address**
   - **Allow Access from Anywhere** (0.0.0.0/0) → **Confirm**

3. Left menu → **Database** → **Connect** → **Drivers**
   - Driver: Python → Copy connection string
   - Format: `mongodb+srv://novabot:<password>@cluster0.xxxxx.mongodb.net/`
   - `<password>` ki jagah apna password dalo

---

## 🤖 Step 2 — Telegram Bot Setup

1. **@BotFather** open karo Telegram mein
2. `/newbot` → naam dalo: `NOVA AI`
3. Username: `nova_hindi_ai_bot` (koi bhi available)
4. **Token copy karo** (format: `1234567890:ABCdef...`)

### Bot Commands Set Karo:
BotFather mein `/setcommands` bhejo → apna bot choose karo → yeh paste karo:
```
start - Bot shuru karo
help - Command list dekho
profile - Apni profile
sticker - Random sticker
reset - Memory reset karo
deep - Deep mode ON
normal - Normal mode
plan - Plan details
```

---

## 🔑 Step 3 — Gemini API Key

1. https://makersuite.google.com/app/apikey open karo
2. **"Create API Key"** dabao
3. **Key copy karo** (format: `AIzaSy...`)

---

## 🌐 Step 4 — Render.com Deploy

### 4.1 — GitHub pe upload karo
1. https://github.com → New repository → `nova-ai-bot`
2. Saari files upload karo (ya git use karo)

### 4.2 — Render pe deploy
1. https://render.com → Sign up (GitHub se)
2. **New +** → **Web Service**
3. GitHub repo connect karo
4. Settings:
   - **Name**: `nova-ai-bot`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free

### 4.3 — Environment Variables add karo
Render dashboard mein → **Environment** tab → Add karo:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | Aapka bot token |
| `GEMINI_API_KEY` | Aapka Gemini key |
| `MONGO_URI` | MongoDB connection string |
| `ADMIN_IDS` | Aapka Telegram ID (e.g. `987654321`) |
| `ADMIN_USERNAME` | Aapka Telegram username (bina @) |
| `RENDER_URL` | Deploy hone ke baad milega (next step) |

### 4.4 — Deploy karo
- **"Create Web Service"** dabao
- Deploy hoga (3-5 minute)
- URL milega: `https://nova-ai-bot.onrender.com`

### 4.5 — RENDER_URL update karo
- Milne wala URL `RENDER_URL` environment variable mein dalo
- **Save Changes** → **Manual Deploy**

---

## 🎮 Bot Commands

### 👤 User Commands
| Command | Function |
|---------|----------|
| `/start` | Welcome message + menu |
| `/help` | Full command list |
| `/profile` | Apni profile + usage stats |
| `/sticker` | Random sticker |
| `/reset` | Chat memory clear |
| `/deep` | Deep AI mode ON |
| `/normal` | Normal fast mode |
| `/plan` | Subscription details |

### 🔐 Admin Commands
| Command | Function |
|---------|----------|
| `/broadcast <msg>` | Sabko message bhejo |
| `/ban <id>` | User ban karo |
| `/unban <id>` | User unban karo |
| `/addpremium <id>` | Premium plan do |
| `/removepremium <id>` | Premium hato |
| `/stats` | Full bot statistics |
| `/userlist` | Latest 20 users |

---

## ✨ Features Complete List

| Feature | Status |
|---------|--------|
| 🇮🇳 Hindi AI Chat | ✅ |
| 🧠 Smart Memory (MongoDB) | ✅ |
| 📁 File Analysis (TXT/JSON/PY) | ✅ |
| 🎭 662 Stickers (6 packs) | ✅ |
| 🚫 Spam Protection | ✅ |
| 🔐 Ban/Unban System | ✅ |
| 📊 Daily Usage Tracking | ✅ |
| 👑 Free & Premium Plans | ✅ |
| 📢 Broadcast System | ✅ |
| 📈 Statistics Dashboard | ✅ |
| 🌐 Webhook (Render) | ✅ |
| 🔄 Polling (Local Dev) | ✅ |
| 🆕 New Member Welcome | ✅ |
| 🧠 Deep Conversation Mode | ✅ |
| ⚡ Auto-Fallback Responses | ✅ |

---

## 🔧 Local Testing (Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. .env file banao
cp .env.example .env
# .env file edit karo apni values ke saath

# 3. RENDER_URL blank rakhna (polling mode ke liye)
# config.py ya .env mein: RENDER_URL=

# 4. Bot start karo
python bot.py
```

---

## 🆘 Troubleshooting

**MongoDB connect nahi ho raha:**
- Network Access mein 0.0.0.0/0 allow hai?
- Password mein special characters (@, #, !) hain? URL-encode karo.

**Bot respond nahi kar raha:**
- Render logs check karo
- All environment variables set hain?
- `nova_bot.log` file dekho

**Webhook kaam nahi kar raha:**
- RENDER_URL bilkul sahi format mein hai? (`https://` se shuru)
- Deploy ke baad RENDER_URL update kiya?

---

*NOVA AI v3.0 — MongoDB + Render + Gemini AI*  
*662 Stickers • Hindi Language • 24/7 Uptime*
