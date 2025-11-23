import random
import string
from loader import bot
from data import config
from aiogram.exceptions import TelegramBadRequest

def g_code():
    characters = string.ascii_letters + string.digits  # Letters and digits
    return ''.join(random.sample(characters, 6))

async def check_channel_membership(user_id: int) -> bool:
    for channel in config.REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except TelegramBadRequest:
            # This can happen if the channel is private and the bot is not an admin,
            # or if the channel username is incorrect.
            return False
    return True