# fitness-nutrition-bot
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import openai

# Вставь сюда свои ключи
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

openai.api_key = OPENAI_API_KEY

# Системный промпт — "мозг" бота
SYSTEM_PROMPT = """
Ты профессиональный нутрициолог и фитнес-тренер. Твоя задача — помогать людям быть здоровыми, активными и красивыми.
Ты даешь простые и научно обоснованные советы по питанию, тренировкам и образу жизни. Не используешь диеты и жёсткие ограничения.
Ты внимательный, дружелюбный и мотивирующий помощник.
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Произошла ошибка. Попробуй ещё раз позже.")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен!")
app.run_polling()
