from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai
import os
from flask import Flask, request

# Инициализация OpenAI и Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Инициализация Flask для вебхуков
app = Flask(__name__)

# Бот
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой фитнес- и нутрициолог-бот.")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ' '.join(context.args)
    if not user_message:
        await update.message.reply_text("Напиши вопрос после команды /ask")
        return
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Ты профессиональный нутрициолог и фитнес-тренер, отвечай ясно и с заботой"},
                  {"role": "user", "content": user_message}]
    )
    reply = response['choices'][0]['message']['content']
    await update.message.reply_text(reply)

# Настройка приложения
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", ask))

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        json_str = request.get_data().decode('UTF-8')
        update = Update.de_json(json.loads(json_str), app.bot)
        app.dispatcher.process_update(update)
        return 'ok', 200

# Устанавливаем вебхук
def set_webhook():
    url = "https://your-render-url.onrender.com/webhook"  # Замени на свой URL от Render
    app.bot.set_webhook(url)

if __name__ == '__main__':
    set_webhook()  # Установим вебхук
    app.run(debug=True)
