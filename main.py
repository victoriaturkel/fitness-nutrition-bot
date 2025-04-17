import os
import openai
from quart import Quart, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Quart-приложение
app = Quart(__name__)
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['PROVIDE_AUTOMATIC_OPTIONS'] = False  # Добавлено для предотвращения ошибки

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

# Webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

# Установка webhook
@app.before_serving
async def setup():
    await telegram_app.bot.set_webhook("https://fitness-nutrition-bot-7.onrender.com/webhook")

if __name__ == "__main__":
    import asyncio
    port = int(os.environ.get("PORT", 5000))
    asyncio.create_task(telegram_app.initialize())
    app.run(host="0.0.0.0", port=port)
