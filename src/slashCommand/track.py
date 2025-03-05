from src.core.addRepo import add_repo_group, add_repo_private
from src.core.botHandler import admin_only
from src.core.botSetup import bot
from telebot.types import Message
from githubAPI.githubAPI import validateGithubURL
import logging

logging.info(f"Added {__name__}")


@bot.message_handler(commands=['track'])
@admin_only
async def add_repo(message: Message):
    text = message.text.split(' ')
    if len(text) < 2 or not validateGithubURL(text[1]):
        await bot.reply_to(message, f"""❌ Please provide the correct repository name and File Extension separated by space. Example:\n `/track https://github.com/username/repo_name .apk`""", parse_mode='Markdown')
        return
    if message.chat.type == "private":
        await add_repo_private(message, text, bot)
        return
    if message.chat.type in ["group", "supergroup"]:
        await add_repo_group(message, text, bot)
        return
