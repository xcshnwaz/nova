import random
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger("NOVA-AI")

SYSTEM_PROMPT = """Tu NOVA AI hai — ek premium, modern aur intelligent Hindi Telegram chatbot.

RULES (hamesha follow kar):
1. SIRF HINDI mein jawab de (thoda Hinglish allowed hai)
2. Replies SHORT aur CLEAR rakh — 2-4 lines max
3. Friendly, warm aur professional tone rakh
4. Emojis thoda use kar — zyada nahi
5. Har jawab helpful aur accurate ho
6. Agar kuch pata nahi, honestly bol
7. Negative ya harmful content mat de
8. User ko feel karana chahiye ki tu unka dost hai

PERSONALITY: Smart, caring, honest, witty, direct."""

DEEP_PROMPT = """Tu NOVA AI hai — ek premium Hindi Telegram chatbot. DEEP MODE ACTIVE HAI.

RULES:
1. SIRF HINDI mein jawab de
2. Detailed, thoughtful aur comprehensive replies de (6-12 lines)
3. Multiple perspectives aur examples use kar
4. Professional yet friendly tone
5. Structured response de — points ya paragraphs mein

PERSONALITY: Expert, thorough, insightful."""

FALLBACKS = [
    "Oops! Thodi technical problem aayi. Ek baar phir try karo! 🙏",
    "Maafi chahta hoon, abhi server slow hai. Dobara bhejo! 😊",
    "Abhi AI busy hai. 2 second ruko aur phir try karo! 🔄",
    "Kuch gadbad ho gayi. Chinta mat karo, phir se likho! 💪",
]


class AIEngine:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.85,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        )
        logger.info("✅ Gemini AI Engine ready!")

    async def chat(self, user_message: str, history: list, deep_mode: bool = False) -> str:
        try:
            system = DEEP_PROMPT if deep_mode else SYSTEM_PROMPT
            chat_history = []
            for entry in history[-12:]:
                role = "user" if entry["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [entry["content"]]})

            convo = self.model.start_chat(history=chat_history)

            if not chat_history:
                full_msg = f"{system}\n\nUser ka message: {user_message}"
            else:
                full_msg = user_message

            response = convo.send_message(full_msg)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return random.choice(FALLBACKS)

    async def summarize_file(self, filename: str, content: str) -> str:
        try:
            prompt = f"""
File naam: {filename}
Content:
{content[:3000]}

Iska ek clear summary HINDI mein do.
- Key points bullet points mein
- Max 200 words
- Simple aur clear bhasha
"""
            response = self.model.generate_content(prompt)
            return f"📄 *File: `{filename}`*\n\n{response.text.strip()}"
        except Exception as e:
            logger.error(f"File summary error: {e}")
            return f"📄 *File `{filename}` mili!*\n\nSummary abhi nahi ban sakti. Baad mein try karo."

    async def answer_question(self, question: str) -> str:
        try:
            prompt = f"Yeh question ka jawab Hindi mein do, short aur accurate:\n{question}"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"QA error: {e}")
            return random.choice(FALLBACKS)
