from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Недвижимость"),
         KeyboardButton(text="🏢 Бизнес"),
         KeyboardButton(text="💳 ВНЖ")],
        [KeyboardButton(text="💰 Калькулятор"),
         KeyboardButton(text="📚 Гайды / Ошибки"),
         KeyboardButton(text="🗓 30-мин консультация")],
    ],
    resize_keyboard=True
)

# поделиться телефоном
phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Поделиться телефоном", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# да / нет
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# кнопка «Посчитать лицензию»
calc_button_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Посчитать лицензию", callback_data="calc_start")]
])
# ---------- Кнопочные ответы для квизов ----------

# 1) Company type
kb_company = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Free Zone"), KeyboardButton(text="Mainland")]],
    resize_keyboard=True, one_time_keyboard=True
)

# 2) Yes / No (уже есть yes_no_kb)

# 3) Budget ranges
kb_budget_biz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="до 50 000"), KeyboardButton(text="50–150 000")],
        [KeyboardButton(text="150–300 000"), KeyboardButton(text="300 000+")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)

kb_budget_estate = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="до 500k AED"), KeyboardButton(text="500k – 1 M")],
        [KeyboardButton(text="1 – 3 M"), KeyboardButton(text="3 M+")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)

# 4) Timeframe
kb_timeframe = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1–3 мес"), KeyboardButton(text="3–6 мес")],
        [KeyboardButton(text="6–12 мес"), KeyboardButton(text="> 12 мес")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)

# 5) Payment method
kb_pay = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Cash"), KeyboardButton(text="Mortgage")],
        [KeyboardButton(text="Crypto"), KeyboardButton(text="Другое")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)

# 6) Visas 0-10 (inline)
kb_visas = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=str(n), callback_data=f"vis_{n}") for n in range(0,6)],
    [InlineKeyboardButton(text=str(n), callback_data=f"vis_{n}") for n in range(6,11)],
])

# --- популярные ниши бизнеса (10) ---
kb_niche = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Retail (FMCG)"), KeyboardButton(text="Beauty & Wellness")],
        [KeyboardButton(text="Food & Beverage"), KeyboardButton(text="IT-консалтинг")],
        [KeyboardButton(text="Digital-маркетинг"), KeyboardButton(text="Logistics")],
        [KeyboardButton(text="Healthcare"), KeyboardButton(text="FinTech")],
        [KeyboardButton(text="Tourism & Hospitality"), KeyboardButton(text="Другое")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- inline-клавиатура: визы 0-10 ---
kb_visas = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=str(n), callback_data=f"vis_{n}") for n in range(0,6)],
    [InlineKeyboardButton(text=str(n), callback_data=f"vis_{n}") for n in range(6,11)],
])

# Клавиатура популярных районов Дубая
kb_locations = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Dubai Marina"), KeyboardButton(text="Downtown")],
        [KeyboardButton(text="Palm Jumeirah"), KeyboardButton(text="JVC")],
        [KeyboardButton(text="Business Bay"), KeyboardButton(text="Другое")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)

# Клавиатура бюджетов недвижимости
kb_estate_choice = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🗓 Консультация"),
               KeyboardButton(text="▶️ Начать квиз")]],
    resize_keyboard=True, one_time_keyboard=True
)
kb_budget_estate = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="до 500k AED"), KeyboardButton(text="500k – 1 M")],
        [KeyboardButton(text="1 – 3 M"),     KeyboardButton(text="3 M+")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

kb_consult_estate = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="🗓 Записаться на 30-мин консультацию (Недвижимость)",
        url="https://calendar.app.google/NdvDfneG6RQev5ea9")]
])

kb_consult_biz = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="🗓 Записаться на 30-мин консультацию (Бизнес)",
        url="https://calendar.app.google/i4p9fKSxSUQv29Zh6")]
])
# Квиз-консультация: тему выбираем одной кнопкой
kb_consult_topic = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Недвижимость"), KeyboardButton(text="Бизнес")],
        [KeyboardButton(text="ВНЖ / Резиденство")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)
# ---------- список популярных Free-Zone ----------
kb_freezones = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="DMCC"),          KeyboardButton(text="IFZA")],
        [KeyboardButton(text="SPC Free Zone"), KeyboardButton(text="RAKEZ")],
        [KeyboardButton(text="Meydan FZ"),     KeyboardButton(text="KIZAD")],
        [KeyboardButton(text="Не уверен / Не знаю")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
# ─── Период запуска/инвестиций ───
kb_plan_time = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="В этом месяце"), KeyboardButton(text="1-3 месяца")],
        [KeyboardButton(text="3-6 месяцев"),   KeyboardButton(text="Пока не решил")],
    ],
    resize_keyboard=True, one_time_keyboard=True
)

# ─── Меню выбора в «Бизнес» ───
kb_business_choice = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💬 Консультация"),
               KeyboardButton(text="💰 Узнать стоимость")]],
    resize_keyboard=True, one_time_keyboard=True
)

# ─── Главное меню (без «Гайды») ───
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Недвижимость"), KeyboardButton(text="🏢 Бизнес")],
        [KeyboardButton(text="💰 Калькулятор"),  KeyboardButton(text="🗓 30-мин консультация")],
    ],
    resize_keyboard=True
)
# ---------- выбор после нажатия "🏢 Бизнес" ----------
kb_business_choice = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💬 Консультация"),
               KeyboardButton(text="💰 Узнать стоимость")]],
    resize_keyboard=True, one_time_keyboard=True
)

# ---------- выбор после нажатия "🏠 Недвижимость" ----------
kb_estate_choice = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="▶️ Начать квиз"),
               KeyboardButton(text="🗓 Консультация")]],
    resize_keyboard=True, one_time_keyboard=True
)