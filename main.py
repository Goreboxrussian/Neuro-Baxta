import os
import asyncio
import logging
import requests
import json
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

context = []

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer(
        "👋 Привет! Я НейроБахта — твой AI помощник на базе Qwen 30B.
"
        "Просто задай мне вопрос. Чтобы сбросить контекст, напиши /reset."
    )

@dp.message(F.text == "/reset")
async def reset_cmd(message: Message):
    context.clear()
    await message.answer("🔄 Контекст сброшен! Можем начать с чистого листа.")

@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    context.append({"role": "user", "content": user_text})

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "qwen/qwen3-30b-a3b:free",
                "messages": context,
            })
        )
        result = response.json()
        bot_reply = result["choices"][0]["message"]["content"]
        context.append({"role": "assistant", "content": bot_reply})
        await message.answer(bot_reply)
    except Exception as e:
        logging.exception(e)
        await message.answer("Произошла ошибка при получении ответа от модели.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
