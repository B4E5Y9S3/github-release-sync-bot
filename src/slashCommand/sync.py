from src.core.botSetup import bot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import os
import aiohttp
import json
import aiofiles
from githubAPI.githubAPI import isLatestDownloadUrl
from src.core.botHandler import admin_only, readData, getDatabaseName
from src.core.commandLock import isUserLocked, commandLock, commandUnlock
import logging

logging.info(f"Added {__name__}")


@bot.message_handler(commands=['sync'])
@admin_only
async def sync_repos(message: Message):
    databaseName = getDatabaseName(message.chat.type)
    chatID = message.chat.id
    chatInfo = await bot.get_chat(chatID)
    userLock = isUserLocked(message)

    if userLock:
        print(f'{message.from_user.first_name} is locked')
        userLockMsg = await bot.reply_to(message, "❌ You cannot use this command for now. Let your previous command complete first.")
        await asyncio.sleep(3)
        await bot.delete_message(chatID, userLockMsg.message_id)
        return

    commandLock(message)
    try:
        data = await readData(databaseName)
        repos = data.get(str(chatID), {}).get('tracking', [])

        if not repos:
            await bot.reply_to(message, "No Repositories are being tracked... start tracking by using `/track` command.", parse_mode='Markdown')
            return

        syncingMessage = await bot.reply_to(message, "Syncing the repositories...")
        os.makedirs("temp", exist_ok=True)  # Ensure temp directory exists

        async with aiohttp.ClientSession() as session:
            for index, repo in enumerate(repos):
                downloadURL, repoURL, fileFormat, chatUploadLink, repoName = (
                    repo.get('downloadURL'), repo.get('repoURL'), repo.get(
                        'fileFormat'), repo.get('chatUploadLink'), repo.get('repoName')
                )

                if downloadURL and message.chat.type != "private" and isLatestDownloadUrl(repoURL, fileFormat, downloadURL) and chatUploadLink:
                    print(f"✅ No new files found for {repoName}")
                    keyboard = InlineKeyboardMarkup().add(
                        InlineKeyboardButton("Open Link", url=chatUploadLink)
                    )
                    await bot.send_message(chatID, f"Latest file already uploaded.\n```{repoName} {repoURL}```", parse_mode='Markdown', reply_markup=keyboard)
                    continue

                if not downloadURL:
                    print(
                        f"❌ Files with {fileFormat} not found on the repo `{repoURL}`")
                    await bot.reply_to(message, f"❌ Files with {fileFormat} not found on the repo `{repoURL}`", parse_mode='Markdown')
                    continue

                file_name = downloadURL.split('/')[-1]
                temp_path = f"temp/{file_name}"

                try:
                    async with session.get(downloadURL) as response:
                        if response.status != 200:
                            raise Exception(
                                f"Failed to download file from {repoURL}")

                        with open(temp_path, "wb") as file:
                            file.write(await response.read())

                    with open(temp_path, "rb") as file:
                        print(
                            f"Sending file to @{message.from_user.first_name}")
                        fileSendingMsg = await bot.send_document(chatID, file, caption=f"Latest release file for {repoName}")

                        data[str(
                            chatID)]['tracking'][index]['chatUploadLink'] = f"https://t.me/{chatInfo.username}/{fileSendingMsg.message_id}"
                        async with aiofiles.open(f"src/data/{databaseName}.json", 'w') as f:
                            await f.write(json.dumps(data))

                except Exception as e:
                    await bot.reply_to(message, f"❌ An error occurred: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        await bot.delete_message(chatID, syncingMessage.message_id)
        await bot.reply_to(message, "Syncing Completed!")

    except Exception as e:
        await bot.reply_to(message, f"❌ Critical error occurred: {e}")

    finally:
        commandUnlock(message)
