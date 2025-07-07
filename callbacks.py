python\nfrom aiogram.filters.callback_data import CallbackData\n\nclass CalcData(CallbackData, prefix=\"calc\"):\n    visas: int\n    office: int\n    bank: int\n    ctype: str  # FZ / ML\n
