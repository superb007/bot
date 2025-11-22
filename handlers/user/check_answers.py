from pyexpat.errors import messages

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from keyboards.keyboard import user_markup, main_markup, num_quests
from loader import db
from states import check_states
from data import config
from aiogram.filters import Command
from keyboards.inline import confirm_user, all_checked, one_checked, confirm_admin

user_router = Router()

@user_router.message(Command("check"))
@user_router.message(F.text == config.check_ans)
async def receive_code(message: types.Message, state: FSMContext):
    await state.set_state(check_states.code)
    await message.answer("Please, enter the code to the test", reply_markup=main_markup)

@user_router.message(check_states.code)
async def check_code(message: types.Message, state: FSMContext):
    code = message.text[message.text.find("-")+1:] if "code" in message.text else message.text
    raw = db.fetchone("SELECT * FROM exams WHERE running = 1 AND code = ?", (code,))
    if raw is None:
        await message.answer("No active exam found with this code", reply_markup=main_markup)
    else:
        alr = db.fetchone("SELECT * FROM submissions WHERE userid = ? AND exid = ?", (message.chat.id, raw[0]))
        if alr is None:
            await state.update_data(correct=raw[5])
            await state.update_data(num_quest=raw[4])
            await state.update_data(exid=raw[0])
            response = f"<b>Title:</b> {raw[2]}"
            response += f"\n<b>Description:</b> {raw[3]}" if raw[3]!="__skip" else ""
            response += f"\n<b>Number of questions:</b> {raw[4]}"
            await state.set_state(check_states.receiving)
            await message.answer(response, reply_markup=main_markup)
            await state.update_data(mode=1)
            await state.update_data(current=1)
            await state.update_data(myans="")
            await message.answer("You can send your answers in either of the following ways. Change as you please and send your answers:", reply_markup=all_checked)
        else:
            response = f"<b>Title:</b> {raw[2]}"
            response += f"\n<b>Description:</b> {raw[3]}" if raw[3] != "__skip" else ""
            response += f"\n<b>Number of questions:</b> {raw[4]}"
            response += "\n\n<b>⚠️ You already submitted your answers to this test. You can see your results from 📊 Results section</b>"
            await message.answer(response, reply_markup=user_markup)
            await state.clear()
        return 1

@user_router.callback_query(check_states.receiving)
async def process_checking(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    n = data["current"]
    if callback.data == "all_at_one_checked":
        await callback.answer("Already chosen")
    elif callback.data == "one_by_one":
        await callback.answer("One by one")
        await state.update_data(mode=2)
        await callback.message.answer(f"Send the answer for question number <b>{n}</b>")
        await callback.message.edit_reply_markup(reply_markup=one_checked)
    elif callback.data == "one_by_one_checked":
        await callback.answer("Already chosen")
    elif callback.data == "all_at_one":
        await callback.answer("All at one")
        await state.update_data(mode=1)
        await callback.message.answer(
            f"<b>{n - 1}</b> answers were given with one-by-one method. Please, send the others, starting with the answer for question number {n}, at once.")
        await callback.message.edit_reply_markup(reply_markup=all_checked)

# async def receive_ans(message: types.Message, state: FSMContext):
#     alr = db.fetchone("SELECT correct FROM current")
#     if alr is not None:
#         answered = db.fetchone("SELECT answered FROM user WHERE idx = ?", (message.from_user.id,))
#         if answered is not None:
#             answered = int(answered[0])
#             await message.answer(f"You have already answered! Your result is\nCorrect answers: {answered} out of {len(alr[0])}\nPercentage: {round(100*answered/len(alr[0]), 2)}%")
#         else:
#             await message.answer("Send the correct answers in this format:\n\t<code>abcabc...</code>")
#             await state.set_state(check_states.receiving)
#     else:
#         await message.answer("There is no test active right now")

@user_router.message(check_states.receiving)
async def check_answers(message: types.Message, state: FSMContext):
    # data = await state.get_data()
    # option = int(db.fetchone("SELECT option FROM current")[0])
    # await state.update_data(corr=corr)
    # raw = message.text.lower()
    # num = len(raw)
    # legit = len(corr) == num
    # for i in raw:
    #     if i not in "abcdefghijklmnopqrstuvwxyz"[:option]:
    #         legit = False
    #         break
    # if legit:
    #     response = f"Can you confirm your answers are as follows:\n"
    #     for i in range(num):
    #         response += f"{i+1}.{raw[i].upper()}"
    #         if i != num-1:
    #             response += "__"
    #     await message.reply(response, reply_markup=confirm_user)
    #     await state.update_data(user_ans=raw)
    #     await state.set_state(check_states.confirm)
    # else:
    #     await message.answer("The answer include an option that's not legit or the number of answers is not quite right")
#dsaskfljds kf
    data = await state.get_data()
    cnt = data["current"]
    n_questions = int(data["num_quest"])
    if data["mode"] == 1:
        raw = message.text.split("\n")
        myans = data["myans"]
        for line in range(len(raw)):
            if raw[line] != "":
                myans += ("__" if cnt>1 else "") + raw[line]
                cnt += 1
        print(myans)
        if cnt == n_questions + 1:
            await state.update_data(myans=myans)
            await state.set_state(check_states.confirm)
            await message.answer(f"Can you confirm your actions?", reply_markup=confirm_user)
        else:
            await message.answer(
                "The number of questions doesn't match the entered value. Please, enter correct number of answers or change the number of questions.",reply_markup=num_quests)
    else:
        myans = data["myans"]
        myans += ("__" if cnt > 1 else "") + message.text
        await state.update_data(myans=myans)
        if cnt == n_questions:
            await state.set_state(check_states.confirm)
            await message.answer("You have done entering all the answers. Can you confirm your actions?",reply_markup=confirm_user)
        else:
            cnt += 1
            await state.update_data(current=cnt)
            await message.answer(f"Send the answer for question number <b>{cnt}</b>")

@user_router.callback_query(check_states.confirm)
async def confirm(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "user_confirm":
        data = await state.get_data()
        corr = list(data["correct"].split("__"))
        print(corr)
        user_ans = list(data['myans'].split("__"))
        print(user_ans)
        num_corr = 0
        for i in range(len(corr)):
            num_corr += corr[i] == user_ans[i]
        db.query("INSERT INTO submissions(exid, userid, date, corr) VALUES (?, ?, CURRENT_TIMESTAMP, ?)", (data["exid"], callback.from_user.id, num_corr))
        await callback.message.answer(f"Your result is\nCorrect answers: {num_corr} out of {len(corr)}\nPercentage: {round(100*num_corr/len(user_ans), 2)}%")
        await callback.answer("Confirmed")
        await state.clear()
    elif callback.data == "user_cancel":
        await callback.message.answer("The checking has been cancelled. You can resend your answers.")
        await callback.answer("Cancelled")
    await callback.message.delete()