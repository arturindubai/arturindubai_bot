from aiogram.fsm.state import StatesGroup, State

# -------- Недвижимость --------
class EstateForm(StatesGroup):
    budget     = State()
    location   = State()
    timeframe  = State()
    email      = State()
    phone      = State()

# -------- Бизнес --------
class BizForm(StatesGroup):
    company_type = State()   # Free Zone / Mainland
    niche        = State()
    residents    = State()   # учредители-резиденты?
    visas        = State()   # inline 0-10
    office       = State()
    freezone  = State()   # ← ОБЯЗАТЕЛЕН
    corp_account = State()
    email        = State()
    phone        = State()

class ConsultForm(StatesGroup):
    topic   = State()   # Недвижимость / Бизнес / ВНЖ
    name    = State()
    email   = State()
    phone   = State()