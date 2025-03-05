import os
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TOKEN')

bot = AsyncTeleBot(API_TOKEN)
