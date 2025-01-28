from bot import print_log, add_repo_private, add_repo_group, readData, removeData, getDatabaseName, admin_only
from githubAPI import validateGithubURL, isLatestDownloadUrl
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import os
import aiohttp
from bot.botSetup import bot
from bot.commandLock import commandLock, isUserLocked, commandUnlock
import json
import aiofiles


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, "Hello, I am a bot Designed to help syncing the Github repo releases files!")


@bot.message_handler(commands=['track'])
@admin_only
async def add_repo(message: Message):
    print_log(message)
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


@bot.message_handler(commands=['untrack'])
@admin_only
async def remove_repo(message: Message):
    print_log(message)
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


@bot.message_handler(commands=['list'])
async def list_tracking_repos(message: Message):
    print_log(message)
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


@bot.message_handler(commands=['sync'])
@admin_only
async def sync_repos(message: Message):
    print_log(message)
    databaseName = getDatabaseName(message.chat.type)
    chatID = message.chat.id
    data = await readData(databaseName)
    repos = data[str(chatID)]['tracking']
    userLock = isUserLocked(message)
    chatInfo = await bot.get_chat(chatID)
    if userLock:
        print(f'{message.from_user.first_name} is locked')
        userLockMsg = await bot.reply_to(message, "❌ You cannot use this command for now. Let your previous command complete first.")
        await asyncio.sleep(3)
        await bot.delete_message(chatID, userLockMsg.message_id)
        return

    commandLock(message)
    if len(repos) == 0:
        await bot.reply_to(message, "No Repositories are being tracked... start tracking by using `/track` command.", parse_mode='Markdown')
        return

    syncingMessage = await bot.reply_to(message, "Syncing the repositories...")

    for index, repo in enumerate(repos):
        downloadURL = repo['downloadURL']
        if downloadURL and message.chat.type != "private" and isLatestDownloadUrl(repo['repoURL'], repo['fileFormat'], downloadURL) and repo['chatUploadLink'] != '':
            print(f"✅ No new files found for {repo['repoName']}")
            keyboard = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                "Open Link", url=repo['chatUploadLink'])
            keyboard.add(button)
            await bot.send_message(chatID, f"Latest file already uploaded.\n```{repo['repoName']} {repo['repoURL']}```", parse_mode='Markdown', reply_markup=keyboard)
            continue

        if not downloadURL:
            print(f"❌ Files with {repo['fileFormat']} not found on the repo `{
                  repo['repoURL']}`")
            await bot.reply_to(message, f"❌ Files with {repo['fileFormat']} not found on the repo `{repo['repoURL']}`", parse_mode='Markdown')
            continue

        try:
            # Download the file using aiohttp
            # Extract file name from URL
            file_name = downloadURL.split('/')[-1]
            temp_path = f"temp/{file_name}"  # Save in a temporary folder
            # Ensure the temp directory exists
            os.makedirs("temp", exist_ok=True)

            async with aiohttp.ClientSession() as session:
                print(f"Downloading file from {downloadURL}")
                async with session.get(downloadURL) as response:
                    if response.status == 200:
                        with open(temp_path, "wb") as file:
                            file.write(await response.read())
                    else:
                        print('Failed to download file')
                        await bot.reply_to(message, f"❌ Failed to download file from `{repo['repoURL']}`.")
                        continue

            # Send the downloaded file to the chat
            with open(temp_path, "rb") as file:
                print(f"Sending file to {message.chat.first_name}")
                fileSendingMsg = await bot.send_document(chatID, file, caption=f"Latest release file for {repo['repoName']}")
                async with aiofiles.open(f"bot/data/{databaseName}.json", 'w') as f:
                    data[str(
                        chatID)]['tracking'][index]['chatUploadLink'] = f"https://t.me/{chatInfo.username}/{fileSendingMsg.message_id}"
                    await f.write(json.dumps(data))

            # Optionally, clean up the temporary file after sending
            os.remove(temp_path)

        except Exception as e:
            await bot.reply_to(message, f"❌ An error occurred: {e}")
            continue
        finally:
            await session.close()
            print('Session closed')
    await bot.delete_message(chatID, syncingMessage.message_id)
    await bot.reply_to(message, "Syncing Completed!")
    commandUnlock(message)


if __name__ == '__main__':
    print('bot initialized...')
    asyncio.run(bot.polling())
