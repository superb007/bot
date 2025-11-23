from aiogram import types
from data.config import REQUIRED_CHANNELS

def get_join_channels_keyboard():
    keyboard = []
    for channel in REQUIRED_CHANNELS:
        # Assuming channel username starts with @
        url_channel = channel[1:] if channel.startswith('@') else channel
        keyboard.append([types.InlineKeyboardButton(text=f"Join {channel}", url=f"https://t.me/{url_channel}")])
    
    keyboard.append([types.InlineKeyboardButton(text="✅ I've Joined", callback_data="check_subscription")])
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
