from aiogram import Router, F, types
from keyboards.inline import exam_con
from states.r_exams_states import del_states, end_states
from aiogram.fsm.context import FSMContext

from filters import AdminFilter
from aiogram.filters import Command
from loader import db
from data import config

arch = Router()
arch.message.filter(AdminFilter())
arch.callback_query.filter(AdminFilter())

@arch.message(Command("archive"))
@arch.message(F.text == config.archive)
async def show_archive(message: types.Message):
    r_exams = db.fetchall("SELECT * FROM exams WHERE running = 0")
    if len(r_exams) == 0:
        await message.answer("There is no exams archived")
        return
    for exam in r_exams:
        response = f"<b>Title:</b> {exam[2]}"
        response += f"\n<b>Description:</b> {exam[3]}" if exam[3] != "__skip" else ""
        response += f"\n<b>Number of questions:</b> {exam[4]}"
        btn = [
            [
                types.InlineKeyboardButton(text=config.nm_ans, callback_data=f"show_results_{exam[0]}"),
                types.InlineKeyboardButton(text=config.shw_ans, callback_data=f"show_ans_{exam[0]}"),
            ]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=btn)
        await message.answer(response, reply_markup=markup)
    await message.reply("These are the tests in the archive")

@arch.callback_query()
async def process_utils(callback: types.CallbackQuery, state: FSMContext):
    response =""
    if callback.data.startswith("show_results_"):
        exid = callback.data.split("_")[2]
        submissions = db.fetchall("SELECT * FROM submissions WHERE exid = ? ORDER BY corr DESC, date", (exid,))
        # print(submissions)
        if len(submissions) == 0:
            await callback.answer("No submission yet")
            await callback.message.reply("No submission found for the test")
            return
        response = "These were the top results for the test:\nPlace - Name - Correct answers"
        for sub in range(len(submissions)):
            user_info = db.fetchone("SELECT * FROM user WHERE userid = ?", (submissions[sub][2],))

            # Logic to determine the medal icon
            place_icon = "🥇" if sub == 0 else "🥈" if sub == 1 else "🥉" if sub == 2 else sub + 1

            # Using single quotes '' inside the f-string to avoid syntax errors
            if user_info[3] != "None":
                response += f"\n{place_icon} - <a href='https://t.me/{user_info[3]}'><b>{user_info[2]}</b></a> - {submissions[sub][4]}"
            else:
                response += f"\n{place_icon} - <b>{user_info[2]}</b> - {submissions[sub][4]}"  # Added score here too for consistency

            # FIXED: This line must be OUTSIDE the for loop (aligned with the 'for' keyword)

    elif callback.data.startswith("show_ans_"):
        exid = callback.data.split("_")[2]
        correct = list(db.fetchone("SELECT correct FROM exams WHERE idx = ?", (exid,))[0].split("__"))
        response = "✅ The correct solutions for the test were as follows:"
        for i in range(len(correct)):
            response += f"\n<b># {i+1}</b>: {correct[i]}"
    await callback.message.reply(response, disable_web_page_preview=True)
