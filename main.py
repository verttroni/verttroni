import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from groq import Groq

# API Keys
MY_BOT_TOKEN = "8331463803:AAF64o-Jb4IVC8q-gEJEEeaarKDsehWx8AA"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Active!")

def run_health_check():
    # Render ကပေးတဲ့ Port ကိုသုံးဖို့လိုအပ်ပါတယ်
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[{"role": "user", "content": update.message.text}],
            model="llama-3.3-70b-versatile",
        )
        await update.message.reply_text(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Error occurred: {e}")

# ဒီစာကြောင်းမှာ underscore တွေ မှန်ဖို့ အရေးကြီးဆုံးပါ
if name == "main":
    # Web server ကို background မှာ run မယ်
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # Telegram Bot ကို စမယ်
    app = ApplicationBuilder().token(MY_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("--- Bot starts running on Render 24/7 ---")
    app.run_polling()
