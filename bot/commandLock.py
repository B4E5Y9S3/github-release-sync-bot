from telebot.types import Message

lockedUser = {}


def commandLock(message: Message):
    if message.from_user.id not in lockedUser:
        lockedUser[message.from_user.id] = True


def isUserLocked(message: Message):
    if message.from_user.id in lockedUser:
        return True


def commandUnlock(message: Message):
    if message.from_user.id in lockedUser:
        del lockedUser[message.from_user.id]
