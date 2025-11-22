from aiogram.fsm.state import State, StatesGroup

class create_states(StatesGroup):
    title = State()
    about = State()
    num_quest = State()
    correct_answer = State()
    confirm = State()
