from bot.botHandler import print_log, add_repo_private, add_repo_group
from githubAPI.githubAPI import validateGithubURL
from telebot.types import Message
import asyncio

from bot.botSetup import bot

# USER modules


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, "Hello, I am a bot help to sync the Github repo releases file synchronizer!")


@bot.message_handler(commands=['track'])
async def add_repo(message: Message):
    text = message.text.split(' ')
    if len(text) < 2 or not validateGithubURL(text[1]):
        await bot.reply_to(message, """
                           ❌ Please provide the correct repository name and File Extension separated by space.
                           Example: 
                           ```
                           /track https://github.com/username/repo_name .apk
                           ```
                           """, parse_mode='Markdown')
        return
    print_log(message)
    if message.chat.type == "private":
        await add_repo_private(message, text, bot)
        return
    if message.chat.type in ["group", "supergroup"]:
        await add_repo_group(message, text, bot)
        return


if __name__ == '__main__':
    print('bot initialized')
    asyncio.run(bot.polling())
