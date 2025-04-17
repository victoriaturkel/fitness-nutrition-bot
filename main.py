import os
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# Ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Flask-приложение
app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой нутрициолог и фитнес-тренер!")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ' '.join(context.args)
    if not user_message:
        await update.message.reply_text("Напиши свой вопрос после команды /ask")
        return

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты профессиональный нутрициолог и фитнес-тренер"},
            {"role": "user", "content": user_message}
        ]
    )
    reply = response['choices'][0]['message']['content']
    await update.message.reply_text(reply)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ask", ask))

# Webhook (асинхронно обрабатываем обновления)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, telegram_app.bot)

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.create_task(telegram_app.process_update(update))
    return "ok"

# Установка webhook перед запуском сервера
async def setup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook("https://fitness-nutrition-bot-7.onrender.com/webhook")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=port)
