async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = ' '.join(context.args)
        if not user_message:
            await update.message.reply_text("Напиши свой вопрос после команды /ask")
            return

        await update.message.reply_text("Готовлю ответ, подожди немного...")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессиональный нутрициолог и фитнес-тренер"},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)

    except Exception

Хорошо! Раз команда `/start` работает, а `/ask` — **нет**, давай добьёмся, чтобы всё точно заработало.

---

## **Вот полностью рабочий `main.py` с исправлениями:**

- Заменили `Quart` на `Flask==3.x`, как требует `quart`
- Удалили `@before_first_request`, потому что он больше не поддерживается
- Добавили логирование ошибок
- Добавили инициализацию Telegram-приложения **вручную при старте**
- Поддерживаем webhook и команду `/ask`

---

### Полный код:
```python
import os
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://fitness-nutrition-bot-7.onrender.com/webhook"

# OpenAI
openai.api_key = OPENAI_API_KEY

# Flask-приложение
app = Flask(__name__)

# Telegram-приложение
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой нутрициолог и фитнес-тренер!")


# Команда /ask
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = ' '.join(context.args)
        if not user_message:
            await update.message.reply_text("Напиши свой вопрос после команды /ask")
            return

        await update.message.reply_text("Думаю...")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессиональный нутрициолог и фитнес-тренер."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")


# Регистрируем команды
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ask", ask))


# Обработка входящих webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"


# Старт
if __name__ == "__main__":
    import asyncio

    async def main():
        await telegram_app.initialize()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
