import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"Received message: {user_message}")
    print(f"Sending to: {FASTAPI_URL}/api/v1/chat")

    await update.message.reply_text("Searching for exercises... 💪")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{FASTAPI_URL}/api/v1/chat",
                json={"query": user_message, "source": "telegram"}
            )
            data = response.json()

            if response.status_code == 429:
                await update.message.reply_text(
                    "⚠️ Too many requests. Please wait a minute before trying again."
                )
                return

            answer = data.get("answer", {})
            message = answer.get("message", "No response found.")
            image_urls = answer.get("image_urls", [])

            # Send text response
            await update.message.reply_text(message)

            # Send images if available
            for url in image_urls:
                if url:
                    await update.message.reply_photo(photo=url)

            # feedback buttons
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👍 Relevant", callback_data="feedback_relevant"),
                    InlineKeyboardButton("👎 Not Relevant", callback_data="feedback_not_relevant")
                ]
            ])
            await update.message.reply_text("Was this response helpful?", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Something went wrong. Please try again.")


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "feedback_relevant":
        await query.edit_message_text("✅ Thanks for your feedback!")
        # send to FastAPI
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                f"{FASTAPI_URL}/api/v1/feedback",
                json={"feedback": "relevant", "source": "telegram"}
            )
    else:
        await query.edit_message_text("❌ Thanks! We'll work on improving.")
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                f"{FASTAPI_URL}/api/v1/feedback",
                json={"feedback": "not_relevant", "source": "telegram"}
            )



if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_feedback))
    app.run_polling()