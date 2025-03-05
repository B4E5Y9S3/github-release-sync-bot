from src.core.botSetup import bot
from telebot.types import Message
from src.core.botHandler import removeData, getDatabaseName, admin_only
import logging

logging.info(f"Added {__name__}")


@bot.message_handler(commands=['untrack'])
@admin_only
async def remove_repo(message: Message):
    chatID = message.chat.id
    text = message.text.split(' ')
    if len(text) < 2:
        await bot.reply_to(message, f"❌ Please provide the repository *URL* to remove from tracking list. Example:\n `/untrack https://github.com/username/repo_name`", parse_mode='Markdown')
        return
    removedData = await removeData(text[1], chatID, getDatabaseName(message.chat.type))
    if not removedData:
        await bot.reply_to(message, f"Repository {text[1]} is not being tracked.")
        return
    await bot.reply_to(message, f"Repository `{text[1]}` removed from tracking list.", parse_mode='Markdown')
