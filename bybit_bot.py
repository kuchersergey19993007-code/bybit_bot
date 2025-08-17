import os
import requests
import pytz
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Updater, CommandHandler
import logging

# Логирование (Render будет сохранять логи)
logging.basicConfig(level=logging.INFO)

# Достаём токен и чат айди из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Часовой пояс Дублин
tz = pytz.timezone("Europe/Dublin")

bot = Bot(token=TELEGRAM_TOKEN)

def fetch_announcements():
    url = "https://announcements.bybit.com/en-US/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        announcements = []
        for article in soup.find_all("a", class_="article-card"):
            title = article.get_text(strip=True)
            link = "https://announcements.bybit.com" + article.get("href")
            announcements.append({"title": title, "link": link})
        return announcements
    except Exception as e:
        logging.error(f"Ошибка при получении анонсов: {e}")
        return []

def check_announcements(update, context):
    announcements = fetch_announcements()
    if not announcements:
        context.bot.send_message(chat_id=CHAT_ID, text="❌ Не удалось получить анонсы")
        return
    msg = "📢 Последние анонсы Bybit:\n\n"
    for ann in announcements[:5]:
        msg += f"- {ann['title']}\n{ann['link']}\n\n"
    context.bot.send_message(chat_id=CHAT_ID, text=msg)

def start(update, context):
    context.bot.send_message(chat_id=CHAT_ID, text="✅ Бот запущен! Используй /check для проверки анонсов.")

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check", check_announcements))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
