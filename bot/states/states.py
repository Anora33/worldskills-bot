from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Ro'yxatdan o'tish holatlari"""
    full_name = State()
    phone = State()
    competition = State()


class AIChatStates(StatesGroup):
    """AI suhbat holati"""
    asking = State()
