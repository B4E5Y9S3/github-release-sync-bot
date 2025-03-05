from .botHandler import readData, addMoreData, addNewData, isRepoTracked
from telebot.types import Message
from githubAPI import getLatestFile, getLatestRelease


async def add_repo_private(message: Message, text, bot):
    databaseName = 'private'
    chatID = message.chat.id
    latestRelease = getLatestRelease(text[1])
    downloadURL = getLatestFile(
        latestRelease['assets'], text[2])
    try:
        data = await readData(databaseName)
        newData = {"repoName": text[1][text[1].rfind('/') + 1:],
                   "repoURL": text[1], "fileFormat": text[2], "lastSync": '', "downloadURL": downloadURL}
        if str(chatID) not in data:
            print("user not found on the database. adding...")
            await addNewData(newData, chatID, databaseName)
            return await bot.reply_to(message, f"✅ Successfully added the repo to track.")
        repoTracked = await isRepoTracked(newData, chatID, databaseName)
        if repoTracked:
            return await bot.reply_to(message, f"❌ Repo already being tracked.")
        print('user found on the database. updating...')
        await addMoreData(newData, chatID, databaseName)
        await bot.reply_to(message, f"✅ Successfully added the repo to track.")

    except Exception as e:
        print(e)
        await bot.reply_to(message, f"Please Provide details correctly and Try again...")


async def add_repo_group(message: Message, text, bot):
    databaseName = 'group'
    chatID = message.chat.id
    latestRelease = getLatestRelease(text[1])
    downloadURL = getLatestFile(
        latestRelease['assets'], text[2])
    try:
        data = await readData(databaseName)
        newData = {"repoName": text[1][text[1].rfind('/') + 1:],
                   "repoURL": text[1], "fileFormat": text[2], "lastSync": '', "downloadURL": downloadURL, "chatUploadLink": ''}
        if str(chatID) not in data:
            print("Group ID not found on database. adding...")
            await addNewData(newData, chatID, databaseName)
            return await bot.reply_to(message, f"✅ Successfully added the repo to track.")
        repoTracked = await isRepoTracked(newData, chatID, databaseName)
        if repoTracked:
            return await bot.reply_to(message, f"❌ Repo already being tracked.")
        print('Group ID found on the database. updating...')
        await addMoreData(newData, chatID, databaseName)
        await bot.reply_to(message, f"✅ Successfully added the repo to track.")

    except Exception as e:
        print(e)
        await bot.reply_to(message, f"❌ Sorry can't track the repo.")
