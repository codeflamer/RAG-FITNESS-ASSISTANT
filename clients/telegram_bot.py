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

    user = update.effective_user
    username = user.username if user.username else f"{user.first_name} {user.last_name}"
    user_id = str(update.effective_user.id)

    await update.message.reply_text("Searching for exercises... 💪")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{FASTAPI_URL}/api/v1/chat",
                headers={"X-User-ID": user_id},
                json={"query": user_message, "source": "telegram", "user":username}
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
            conversation_id = answer.get("conversation_id","")
            logging.info(f"conversation_id: {conversation_id}")

            # Send text response
            await update.message.reply_text(message)

            # Send images if available
            for url in image_urls:
                if url:
                    await update.message.reply_photo(photo=url)

            # feedback buttons
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👍 Relevant", callback_data=f"rel_{conversation_id}"),
                    InlineKeyboardButton("👎 Not Relevant", callback_data=f"notrel_{conversation_id}")
                ]
            ])
            await update.message.reply_text("Was this response helpful?", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Something went wrong. Please try again.")


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    conversation_id = query.data.split("_")[1]
    logging.info(f"conversation_id-1: {conversation_id}")

    if query.data.startswith("rel_"):
        await query.edit_message_text("✅ Feedback saved!")
        # send to FastAPI
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                f"{FASTAPI_URL}/api/v1/feedback",
                json={"feedback": "relevant", "source": "telegram", "conversation_id":conversation_id}
            )
    else:
        await query.edit_message_text("✅ Feedback saved!")
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                f"{FASTAPI_URL}/api/v1/feedback",
                json={"feedback": "not_relevant", "source": "telegram","conversation_id":conversation_id}
            )



if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_feedback))
    app.run_polling()