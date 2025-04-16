import os
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai

# Настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Создаём Flask-приложение
flask_app = Flask(__name__)

# Создаём Telegram-приложение
bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой нутрициолог и фитнес-тренер!")

# Команда /ask
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

# Добавляем команды
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("ask", ask))

# Webhook обработчик
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok"

# Устанавливаем webhook при запуске
if __name__ == '__main__':
    import asyncio
    async def main():
        webhook_url = "https://your-render-url.onrender.com/webhook"  # замени на свой URL
        await bot_app.bot.set_webhook(webhook_url)
        print("Webhook установлен")

    asyncio.run(main())
    flask_app.run(host="0.0.0.0", port=10000)
