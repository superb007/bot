from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from loader import db
from data import config
from data.config import results
from states.check_states import results_states

res = Router()

@res.message(F.text == config.results)
async def shresults(message: Message, state: FSMContext):
    btn = [
        [
            InlineKeyboardButton(text="Last test", callback_data="last"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btn)
    await state.set_state(results_states.choice)
    await message.answer("Choose which test you want to know the results of or enter the code:", reply_markup=markup)

@res.message(results_states.choice)
async def coderesults(message: Message, state: FSMContext):
    code = message.text
    if len(code) != 6:
        await message.answer("Please enter a valid code.")
    else:
        exam = db.fetchone("SELECT idx, num_questions FROM exams WHERE code = ?", (code,))
        if exam is not None:
            exid, total = exam[0], exam[1]
            # userid = db.fe
            ress = db.fetchone("SELECT corr FROM submissions WHERE exid = ? AND userid = ?", (exid,message.from_user.id))
            await message.answer(f"The number of correct answers: {ress} out of {total}")
        else:
            await message.answer("No exam found with that code")
    await state.clear()


@res.callback_query(results_states.choice)
async def choiceres(callback: CallbackQuery, state: FSMContext):
    if callback.data == "last":
        subm = db.fetchone("SELECT * FROM submissions WHERE userid = ? ORDER BY idx DESC", (callback.from_user.id,))
        if subm is not None:
            total = db.fetchone("SELECT num_questions FROM exams WHERE idx = ?", (subm[1],))[0]
            await callback.message.answer(f"The number of correct answers: {subm[4]} out of {total}")
            await state.clear()
        else:
            await callback.message.answer(f"You have never tried yet")