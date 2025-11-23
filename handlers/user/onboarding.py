from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states.onboarding_states import OnboardingStates
from utils.funs import check_channel_membership
from keyboards.keyboard.user_keyboard import request_contact_markup, user_markup
from loader import db

onboarding_router = Router()

@onboarding_router.callback_query(F.data == "check_subscription")
async def handle_check_subscription(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await check_channel_membership(user_id):
        await callback.message.delete()
        await callback.answer("✅ Thank you for subscribing!", show_alert=True)
        await state.set_state(OnboardingStates.get_name)
        await callback.message.answer("Please enter your name:")
    else:
        await callback.answer("⚠️ You haven't joined all the channels yet. Please join them to continue.", show_alert=True)

@onboarding_router.message(OnboardingStates.get_name)
async def handle_get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OnboardingStates.get_surname)
    await message.answer("Great! Now, please enter your surname:")

@onboarding_router.message(OnboardingStates.get_surname)
async def handle_get_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(OnboardingStates.get_contact)
    await message.answer("Thank you. Finally, please share your contact information by clicking the button below.", reply_markup=request_contact_markup)

@onboarding_router.message(OnboardingStates.get_contact, F.contact)
async def handle_get_contact(message: Message, state: FSMContext):
    contact = message.contact.phone_number
    await state.update_data(contact=contact)
    
    data = await state.get_data()
    user_id = message.from_user.id
    full_name = data.get('name')
    surname = data.get('surname')
    username = message.from_user.username
    
    # Save to database
    db.query(
        "INSERT INTO user (userid, fullname, surname, username, contact, regdate) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (user_id, full_name, surname, username, contact)
    )
    
    await state.clear()
    await message.answer("🎉 Thank you! You have been successfully registered.", reply_markup=user_markup)

@onboarding_router.message(OnboardingStates.get_contact)
async def handle_get_contact_text(message: Message, state: FSMContext):
    # Handle cases where user sends text instead of contact
    await message.answer("Please use the 'Share Contact' button to share your contact information.")
