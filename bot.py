from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ChatAction
from langdetect import detect
import os, asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)
chat_memory = {}
MAX_HISTORY = 5


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I am your AI chatbot. How can I assist you today?"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Help*\n\n"
        "• Just type any message\n"
        "• Supports Hindi, Marathi, Tamil, Telugu\n"
        "• Commands:\n"
        "/start Start bot\n"
        "/help Help menu\n"
        "/about About bot\n"
        "/language Language info",
        parse_mode="Markdown",
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*About*\n\n"
        "This is a multilingual AI chatbot built using:\n"
        "• Python\n"
        "• Telegram Bot API\n"
        "• Google Gemini AI\n\n"
        "Made for a school project 🎓",
        parse_mode="Markdown",
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Supported Languages*\n\n"
        "• Hindi\n"
        "• Marathi\n"
        "• Tamil\n"
        "• Telugu\n\n"
        "Just type in your language!",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    try:
        user_lang = detect(user_message)
    except:
        user_lang = "hi"
    if user_id not in chat_memory:
        chat_memory[user_id] = []

    chat_memory[user_id].append(f"User: {user_message}")
    chat_memory[user_id] = chat_memory[user_id][-MAX_HISTORY:]

    history_text = "\n".join(chat_memory[user_id])

    prompt = (
        f"Reply ONLY in {user_lang} language.\n"
        f"Conversation so far:\n{history_text}\n"
        f"Assistant:"
    )
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    await asyncio.sleep(1.5)

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )
        bot_reply = response.candidates[0].content.parts[0].text

        chat_memory[user_id].append(f"Assistant: {bot_reply}")
        chat_memory[user_id] = chat_memory[user_id][-MAX_HISTORY:]
    except Exception as e:
        print("Gemini Error")
        bot_reply = "Sorry, I am having trouble processing your request right now."

    await update.message.reply_text(bot_reply)


application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about_command))
application.add_handler(CommandHandler("language", language_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

application.run_polling()
