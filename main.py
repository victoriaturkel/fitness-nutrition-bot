import os
import openai
from quart import Quart, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ключи из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Quart-приложение
app = Quart(__name__)
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Команды Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой нутрициолог и фитнес-тренер!")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ' '.join(context.args)
    if not user_message:
        await update.message.reply_text("Напиши свой вопрос после команды /ask")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессиональный нутрициолог и фитнес-тренер"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при запросе к OpenAI: {e}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ask", ask))

# Webhook от Telegram
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

# Установка webhook при старте
@app.before_serving
async def setup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook("https://fitness-nutrition-bot-7.onrender.com/webhook")

# Запуск сервера
if __name__ == "__main__":
    import asyncio
    port = int(os.environ.get("PORT", 5000))
    asyncio.run(app.run_task(host="0.0.0.0", port=port))
