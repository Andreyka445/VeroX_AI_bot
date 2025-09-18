import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# --- конфег OPENROUTER ---
OPENROUTER_API_KEY = "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"
TELEGRAM_BOT_TOKEN = "8436574599:AAGFVLIE5JUiscqNhJByu5QG927DGll1zWw"

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# БЕСПЛАТНЫЕ модели на OpenRouter
FREE_MODELS = {
    "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo (быстрый, бесплатный)",
    "google/gemini-flash-1.5": "Google Gemini Flash 1.5 (качественный, бесплатный)",
    "mistralai/mistral-7b-instruct": "Mistral 7B (бесплатный)",
    "deepseek/deepseek-r1:free": "DeepSeek R1 (бесплатный)",  # Исправлено: правильное название
    "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B (бесплатный)"
}

SELECTED_MODEL = "deepseek/deepseek-r1:free"  # Бесплатная и качественная модель

# --- функция для запроса к OpenRouter API ---
def ask_ai(question):
    """запрос к бесплатной модели через OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-telegram-bot",
        "X-Title": "Telegram AI Bot"
    }

    payload = {
        "model": SELECTED_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты полезный AI-ассистент. Отвечай на русском языке понятно и подробно. Будь дружелюбным и helpful."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }

    try:
        print(f"🔗 Отправка запроса к {SELECTED_MODEL}...")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        print("✅ Успешный ответ от API")
        return result['choices'][0]['message']['content']

    except requests.exceptions.HTTPError as e:
        if response.status_code == 402:
            return "💰 Для этой модели требуется оплата. Использую бесплатный режим."
        return f"❌ Ошибка HTTP: {e}"

    except Exception as e:
        return f"🤖 Ответ AI: Это тестовый режим. Ваш вопрос: '{question}'. Для полной функциональности可能需要 настройка платежей."

# --- ОБРАБОТЧИКИ КОМАНД ТЕЛЕГРАМА ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = f"""
🤖 *AI Бот с бесплатными моделями*

Используемая модель: *DeepSeek R1 (бесплатный)*

💬 Просто напиши мне вопрос - и я помогу!

*Команды:*
/start - начать работу
/help - помощь
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
ℹ️ *Помощь по AI боту*
Зачем тебе помощь для использования ии бота?
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    models_text = "🤖 *Доступные бесплатные модели:*\n\n"
    for model_id, model_desc in FREE_MODELS.items():
        current = " ✅" if model_id == SELECTED_MODEL else ""
        models_text += f"• *{model_id}* - {model_desc}{current}\n"

    await update.message.reply_text(models_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    response = ask_ai(user_message)
    await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

# --- запуск бота ---
async def main_async():
    print("🤖 Запуск AI Telegram бота с бесплатными моделями...")
    print(f"🧠 Используемая модель: {SELECTED_MODEL}")
    print(f"📋 {FREE_MODELS[SELECTED_MODEL]}")

    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("models", models_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)

        print("🔄 Инициализация бота...")
        await application.initialize()
        await application.start()

        print("✅ Бот инициализирован")
        print("📡 Запуск polling...")

        await application.updater.start_polling(
            poll_interval=3.0,
            timeout=30.0,
            drop_pending_updates=True
        )

        print("🎉 Бот запущен и слушает сообщения!")
        print("💬 Напишите боту в Telegram для теста")

        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
    finally:
        try:
            if 'application' in locals():
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
                print("🛑 Бот остановлен")
        except:
            pass

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
