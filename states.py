# states.py  ─── единственный источник состояний FSM
from aiogram.fsm.state import StatesGroup, State

class EstateForm(StatesGroup):
    budget     = State()
    location   = State()
    plan_time  = State()      # Когда планирует инвестировать?
    name       = State()      # Имя клиента
    email      = State()
    phone      = State()

class BizForm(StatesGroup):
    niche        = State()
    company_type = State()
    freezone     = State()
    residents    = State()
    visas        = State()
    office       = State()
    bank         = State()
    plan_time    = State()
    name         = State()    # Имя клиента
    email        = State()
    phone        = State()

class ConsultForm(StatesGroup):
    topic  = State()
    name   = State()
    email  = State()
    phone  = State()