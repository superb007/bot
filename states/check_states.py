from aiogram.fsm.state import State, StatesGroup

class check_states(StatesGroup):
    code = State()
    receiving = State()
    confirm = State()

class results_states(StatesGroup):
    choice = State()