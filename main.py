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

# Flask-приложение
app = Flask(__name__)

# Telegram-приложение
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

# Добавляем команды
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ask", ask))

# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("Получен запрос от Telegram:", data)  # Логируем запрос от Telegram
    update = Update.de_json(data, telegram_app.bot)
    telegram_app.create_task(telegram_app.process_update(update))
    return "ok"

# Установка webhook
async def setup_webhook():
    url = "https://fitness-nutrition-bot-7.onrender.com/webhook"
    await telegram_app.bot.set_webhook(url)

if __name__ == '__main__':
    import asyncio
    # Проверка порта для Render
    port = int(os.environ.get("PORT", 5000))  # если порт не задан, используем 5000
    # Запуск webhook
    asyncio.run(setup_webhook())
    # Запуск Flask-приложения
    app.run(host='0.0.0.0', port=port)
