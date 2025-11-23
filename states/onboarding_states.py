from aiogram.fsm.state import StatesGroup, State

class OnboardingStates(StatesGroup):
    check_channels = State()
    get_name = State()
    get_surname = State()
    get_contact = State()
