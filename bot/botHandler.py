from telebot.types import Message
from functools import wraps
from bot.botSetup import bot
import aiofiles
import json
log = True


def print_log(message: Message):
    if not log:
        return
    print(f"{message.text} - {message.from_user.username} - {message.chat.id}")


async def is_user_admin(chat_id, from_user_id):
    admins = await bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == from_user_id:
            return True  # User is an admin
    return False  # User is not an admin


def admin_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.chat.type != "private":  # Ensure it's a group chat
            is_admin = await is_user_admin(message.chat.id, message.from_user.id)
            if is_admin:
                # Execute the command if the user is an admin
                return await func(message, *args, **kwargs)
            else:
                await bot.reply_to(message, "Don't be a Punk! Admins only. 😒")
        else:
            await func(message, *args, **kwargs)
    return wrapper


async def readData(dataName: str):
    async with aiofiles.open(f'bot/data/{dataName}.json', 'r') as f:
        return json.loads(await f.read())


async def addMoreData(newData: dict, id, dataName: str):
    data = await readData(dataName)
    data[str(id)]['tracking'].append(newData)
    async with aiofiles.open(f'bot/data/{dataName}.json', 'w') as f:
        await f.write(json.dumps(data))
    return True


async def addNewData(newData: dict, id, dataName: str):
    data = await readData(dataName)
    data[str(id)] = {'tracking': [newData]}
    async with aiofiles.open(f'bot/data/{dataName}.json', 'w') as f:
        await f.write(json.dumps(data))
    return True


async def removeData(url: str, id, dataName: str):
    data = await readData(dataName)
    for key in data[str(id)]['tracking']:
        if key['repoURL'] == url:
            data[str(id)]['tracking'].remove(key)
            async with aiofiles.open(f'bot/data/{dataName}.json', 'w') as f:
                await f.write(json.dumps(data))
            return True
    return False


async def isRepoTracked(newData: dict, id, dataName: str):
    data = await readData(dataName)
    for key in data[str(id)]['tracking']:
        return key['repoURL'] == newData['repoURL']


def getDatabaseName(chatType): return "group" if chatType in [
    'group', 'supergroup'] else 'private'
