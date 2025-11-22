from aiogram.fsm.state import State, StatesGroup

class del_states(StatesGroup):
    confirm = State()

class end_states(StatesGroup):
    confirm = State()

class edit_states(StatesGroup):
    name = State()

class edit_about_states(StatesGroup):
    about = State()