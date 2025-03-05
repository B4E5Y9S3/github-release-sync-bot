import asyncio
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sys
from src.core.botSetup import bot
from src.core import *
from src.slashCommand import *


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    logging.debug(f"Received command: {message.text}")
    await bot.send_message(message.chat.id, "Hello, I am a bot Designed to help syncing the Github repo releases files!")


# Define log directory
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

#
logging.getLogger("aiosqlite").setLevel(logging.ERROR)

# Advanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set the base logging level
    # Custom log format
    format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',  # Custom date format
    handlers=[  # Multiple handlers
        logging.StreamHandler(sys.stdout),  # Log to console
        RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),  # Log file
            maxBytes=5 * 1024 * 1024,  # 5MB per log file
            backupCount=3,  # Keep 3 old log files
            encoding='utf-8'
        ),
        TimedRotatingFileHandler(
            # Separate log for timed rotation
            os.path.join(log_dir, 'timed_log.log'),
            when="midnight",  # Rotate at midnight
            interval=1,  # Rotate every 1 day
            backupCount=7,  # Keep the last 7 days of logs
            encoding='utf-8'
        ),
    ]
)

if __name__ == '__main__':
    print('bot initialized...')
    logging.debug("Bot initialized and starting polling...")
    asyncio.run(bot.polling())
