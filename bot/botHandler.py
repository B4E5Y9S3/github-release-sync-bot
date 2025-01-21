from telebot.types import Message
from functools import wraps
from bot.botSetup import bot
import aiofiles
import json
log = True


def print_log(message):
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
    async def wrapper(message, *args, **kwargs):
        if message.chat.type != "private":  # Ensure it's a group chat
            is_admin = await is_user_admin(message.chat.id, message.from_user.id)
            if is_admin:
                # Execute the command if the user is an admin
                return await func(message, *args, **kwargs)
            else:
                await bot.reply_to(message, "Don't be a Punk! Admins only. 😒")
        else:
            await bot.reply_to(
                message, "⚠️ This command is only available in groups."
            )
    return wrapper


async def add_repo_private(message: Message, text, bot):
    try:
        async with aiofiles.open('bot/data/private.json', 'r') as f:
            group_data = json.loads(await f.read())
        if str(message.chat.id) not in group_data:
            print("user not found on the database. adding...")
            group_data[str(message.chat.id)] = {"tracking": [
                {"repoURL": text[1], "fileFormat": text[2]}]}
            async with aiofiles.open('bot/data/private.json', 'w') as f:
                await f.write(json.dumps(group_data))
            return await bot.reply_to(message, f"✅ Successfully added the repo to track.")
        print('user found on the database. updating...')
        group_data[str(message.chat.id)]["tracking"].append(
            {"repoURL": text[1], "fileFormat": text[2]})
        async with aiofiles.open('bot/data/private.json', 'w') as f:
            await f.write(json.dumps(group_data))
        await bot.reply_to(message, f"✅ Successfully added the repo to track.")

    except Exception as e:
        print(e)
        await bot.reply_to(message, f"❌ Sorry can't track the repo.")


@admin_only
async def add_repo_group(message: Message, text, bot):
    try:
        async with aiofiles.open('bot/data/group.json', 'r') as f:
            group_data = json.loads(await f.read())
        if str(message.chat.id) not in group_data:
            print("Group ID not found on database. adding...")
            group_data[str(message.chat.id)] = {"tracking": [
                {"repoURL": text[1], "fileFormat": text[2]}]}
            async with aiofiles.open('bot/data/group.json', 'w') as f:
                await f.write(json.dumps(group_data))
            return await bot.reply_to(message, f"✅ Successfully added the repo to track.")
        print('Group ID found on the database. updating...')
        group_data[str(message.chat.id)]["tracking"].append(
            {"repoURL": text[1], "fileFormat": text[2]})
        async with aiofiles.open('bot/data/group.json', 'w') as f:
            await f.write(json.dumps(group_data))
        await bot.reply_to(message, f"✅ Successfully added the repo to track.")

    except Exception as e:
        print(e)
        await bot.reply_to(message, f"❌ Sorry can't track the repo.")
