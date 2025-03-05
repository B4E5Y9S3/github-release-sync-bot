from telebot.types import Message
from src.core.botSetup import bot
from src.core.botHandler import getDatabaseName, readData
import logging

logging.info(f"Added {__name__}")


@bot.message_handler(commands=['list'])
async def list_tracking_repos(message: Message):
    databaseName = getDatabaseName(message.chat.type)
    data: dict = await readData(databaseName)
    noRepoMsg = "No Repositories are being tracked... start tracking by using `/track` command."
    if not data or str(message.chat.id) not in data:
        await bot.reply_to(message, noRepoMsg, parse_mode='Markdown')
        return
    repos = data[str(message.chat.id)]['tracking']
    if str(message.chat.id) not in data or len(repos) == 0:
        await bot.reply_to(message, noRepoMsg, parse_mode='Markdown')
        return
    message_text = "Tracking the following repositories:\n"
    for repo in repos:
        message_text += f"```{repo['repoName']
                              } {repo['repoURL']} - {repo['fileFormat']}```\n"
    await bot.reply_to(message, message_text, parse_mode='Markdown')
    return
