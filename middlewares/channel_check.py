from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from data.config import ADMINS
from states.onboarding_states import OnboardingStates
from utils.funs import check_channel_membership
from keyboards.inline.onboarding_inline import get_join_channels_keyboard

class ChannelCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # We only want to check messages and callbacks from users, not admins
        if isinstance(event, (Message, CallbackQuery)) and event.from_user.id not in ADMINS:
            user_id = event.from_user.id
            state: FSMContext = data.get('state')
            
            # Don't check users who are in the process of onboarding
            if state:
                current_state = await state.get_state()
                if current_state and current_state.startswith("OnboardingStates"):
                    return await handler(event, data)

            # Check channel membership
            if not await check_channel_membership(user_id):
                message_text = (
                    "To continue using the bot, you must be subscribed to our channels. "
                    "Please subscribe and then click 'I've Joined'."
                )
                # Try to answer callback query first
                if isinstance(event, CallbackQuery):
                    await event.answer("You are not subscribed to all required channels.", show_alert=True)
                    # Also send a message in the chat
                    if event.message:
                        await event.message.answer(message_text, reply_markup=get_join_channels_keyboard())
                else: # It's a Message
                    await event.answer(message_text, reply_markup=get_join_channels_keyboard())
                return # Stop processing the update
        
        # If checks pass, or if not applicable, continue to the handler
        return await handler(event, data)
