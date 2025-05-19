from aiogram.fsm.state import StatesGroup, State 


class Bio(StatesGroup):
    bio = State()
    
    
class PersonState(StatesGroup):
    wait_person = State()


class IsHistory(StatesGroup):
    history = State()


class VoiceModState(StatesGroup):
    wait_voice_mod = State()