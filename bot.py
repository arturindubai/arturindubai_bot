# bot.py — полный файл (июль 2025)
# ---------------------------------

import asyncio
import logging
import os
import re
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

# ---------- .env ----------
load_dotenv(Path(__file__).with_name(".env"))
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found in .env")

# ---------- bot ----------
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ---------- внутренние модули ----------
from keyboards import (
    main_menu, guides_inline_kb, phone_kb, yes_no_kb, calc_button_kb,
    kb_company, kb_timeframe, kb_niche, kb_visas,
    kb_locations, kb_budget_estate, kb_consult_estate, kb_consult_biz, kb_consult_topic,
)
from states import EstateForm, BizForm, ConsultForm
from texts import WELCOME_TEXT, GUIDE_LINKS, FREEZONE_VS_MAINLAND
from sheets import save_lead

# ---------- тарифы и helper-блок ----------
TARIFFS = dict(
    FZ_base=12_000,
    ML_base=18_000,
    visa=3_500,
    office=5_000,
    bank=4_000,
    vat=0.05,
)


def calc_cost(ctype: str, visas: int, office: bool, bank: bool) -> int:
    cost = TARIFFS[f"{ctype}_base"] + visas * TARIFFS["visa"]
    if office:
        cost += TARIFFS["office"]
    if bank:
        cost += TARIFFS["bank"]
    return int(cost * (1 + TARIFFS["vat"]))


# ================= /start =================
@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu)
    await state.clear()


# ================= гайды =================
@dp.message(F.text == "📚 Гайды / Ошибки")
async def show_guides(message: Message):
    await message.answer("Выберите файл:", reply_markup=guides_inline_kb)


@dp.callback_query(F.data.in_(GUIDE_LINKS.keys()))
async def send_guide(cb: CallbackQuery):
    link = GUIDE_LINKS.get(cb.data)
    if link:
        await cb.message.answer(f"✅ Ваш файл:\n{link}")
    await cb.answer()


# ================= квиз «Недвижимость» =================
@dp.message(F.text == "🏠 Недвижимость")
async def est_start(m: Message, state: FSMContext):
    await m.answer("Ваш бюджет:", reply_markup=kb_budget_estate)
    await state.set_state(EstateForm.budget)


@dp.message(EstateForm.budget)
async def est_budget(m: Message, state: FSMContext):
    await state.update_data(budget=m.text)
    await m.answer("Выберите локацию:", reply_markup=kb_locations)
    await state.set_state(EstateForm.location)


@dp.message(EstateForm.location)
async def est_location(m: Message, state: FSMContext):
    await state.update_data(location=m.text)
    await m.answer("Когда планируете покупку?", reply_markup=kb_timeframe)
    await state.set_state(EstateForm.timeframe)


@dp.message(EstateForm.timeframe)
async def est_timeframe(m: Message, state: FSMContext):
    await state.update_data(timeframe=m.text)
    await m.answer("📧 Оставьте e-mail:")
    await state.set_state(EstateForm.email)


# ---------- E-MAIL и ТЕЛЕФОН (Недвижимость) ----------
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

@dp.message(EstateForm.email)
async def est_email(m: Message, state: FSMContext):
    if not EMAIL_RE.match(m.text.strip()):
        return await m.answer(
            "Введите корректный e-mail, например: <code>user@example.com</code>")
    await state.update_data(email=m.text)
    await m.answer("📞 Нажмите кнопку «Поделиться телефоном»", reply_markup=phone_kb)
    await state.set_state(EstateForm.phone)


# принимаем ТОЛЬКО contact-объект
@dp.message(F.contact, EstateForm.phone)
async def est_finish(m: Message, state: FSMContext):
    data = await state.get_data()
    save_lead(
        {"id": m.from_user.id,
         "first_name": m.from_user.first_name,
         "username": m.from_user.username or "",
         "phone": m.contact.phone_number},
        source="estate",
        payload=data,
    )
    await m.answer(
        "🎉 Спасибо! Мы подберём лучшие варианты и свяжемся в ближайшее время.",
        reply_markup=main_menu)
    await state.clear()
    await m.answer(
    "🗓 Хотите обсудить детали лично? Забронируйте 30-мин консультацию:",
    reply_markup=kb_consult_estate
)

# если пользователь ПЫТАЕТСЯ ввести номер руками
@dp.message(~F.contact, EstateForm.phone)
async def est_phone_text(m: Message):
    await m.answer(
        "Пожалуйста, нажмите кнопку «📞 Поделиться телефоном» — так номер передастся корректно.",
        reply_markup=phone_kb)


# ================= квиз «Бизнес» =================
@dp.message(F.text == "🏢 Бизнес")
async def biz_intro(m: Message, state: FSMContext):
    await m.answer(FREEZONE_VS_MAINLAND)
    await m.answer("Выберите тип компании:", reply_markup=kb_company)
    await state.set_state(BizForm.company_type)


@dp.message(BizForm.company_type)
async def biz_company_type(m: Message, state: FSMContext):
    ctype = "FZ" if "free" in m.text.lower() else "ML"
    await state.update_data(company_type=ctype)
    await m.answer("Ниша бизнеса?", reply_markup=kb_niche)
    await state.set_state(BizForm.niche)


@dp.message(BizForm.niche)
async def biz_niche(m: Message, state: FSMContext):
    await state.update_data(niche=m.text)
    await m.answer("Учредители уже резиденты? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.residents)


@dp.message(BizForm.residents)
async def biz_residents(m: Message, state: FSMContext):
    await state.update_data(residents=m.text.lower() == "да")
    await m.answer("Сколько виз требуется?", reply_markup=kb_visas)
    await state.set_state(BizForm.visas)


# ---------- выбор виз: inline кнопка ----------
@dp.callback_query(F.data.startswith("vis_"), BizForm.visas)
async def biz_visas_cb(cb: CallbackQuery, state: FSMContext):
    visas = int(cb.data.split("_")[1])
    await state.update_data(visas=visas)
    await cb.message.edit_reply_markup()
    await cb.message.answer("Нужен офис? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.office)
    await cb.answer()


# ---------- выбор виз: текстовый ввод ----------
@dp.message(BizForm.visas)
async def biz_visas_text(m: Message, state: FSMContext):
    if not m.text.isdigit() or not 0 <= int(m.text) <= 10:
        return await m.answer("Выберите цифру 0-10 кнопкой ниже.")
    await state.update_data(visas=int(m.text))
    await m.answer("Нужен офис? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.office)


@dp.message(BizForm.office)
async def biz_office(m: Message, state: FSMContext):
    await state.update_data(office=m.text.lower() == "да")
    await m.answer("Нужен корпоративный счёт? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.corp_account)


@dp.message(BizForm.corp_account)
async def biz_corp_account(m: Message, state: FSMContext):
    await state.update_data(corp_account=m.text.lower() == "да")
    await m.answer("📧 Ваш e-mail?")
    await state.set_state(BizForm.email)


@dp.message(BizForm.email)
async def biz_email(m: Message, state: FSMContext):
    if not EMAIL_RE.match(m.text.strip()):
        return await m.answer(
            "Введите корректный e-mail, например: <code>founder@example.com</code>")
    await state.update_data(email=m.text)
    await m.answer("📞 Нажмите кнопку «Поделиться телефоном»", reply_markup=phone_kb)
    await state.set_state(BizForm.phone)

@dp.message(~F.contact, BizForm.phone)
async def biz_phone_text(m: Message):
    await m.answer(
        "Пожалуйста, нажмите кнопку «📞 Поделиться телефоном» ниже — это безопасно 👍",
        reply_markup=phone_kb)


# ---------- Калькулятор ----------
@dp.callback_query(F.data == "calc_start")
async def calc_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Сколько виз? (0-10)", reply_markup=kb_visas)
    await state.set_state("calc_visas")
    await cb.answer()


@dp.callback_query(F.data.startswith("vis_"), F.state == "calc_visas")
async def calc_visas_cb(cb: CallbackQuery, state: FSMContext):
    visas = int(cb.data.split("_")[1])
    await state.update_data(calc_visas=visas)
    await cb.message.edit_reply_markup()
    await cb.message.answer("Нужен офис? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state("calc_office")
    await cb.answer()


@dp.message(F.state == "calc_visas")
async def calc_visas_text(m: Message, state: FSMContext):
    if not m.text.isdigit() or not 0 <= int(m.text) <= 10:
        return await m.answer("Введите число 0-10 или нажмите кнопку.")
    await state.update_data(calc_visas=int(m.text))
    await m.answer("Нужен офис? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state("calc_office")


@dp.message(F.state == "calc_office")
async def calc_office(m: Message, state: FSMContext):
    await state.update_data(calc_office=m.text.lower() == "да")
    await m.answer("Нужен корпоративный счёт? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state("calc_bank")


@dp.message(F.state == "calc_bank")
async def calc_bank(m: Message, state: FSMContext):
    await state.update_data(calc_bank=m.text.lower() == "да")
    data = await state.get_data()
    total = calc_cost(
        ctype=data["company_type"],
        visas=data["calc_visas"],
        office=data["calc_office"],
        bank=data["calc_bank"],
    )
    await m.answer(
        f"💸 Ориентировочная стоимость лицензии: <b>AED {total:,}</b>\n\n"
        "📞 Поделитесь телефоном, чтобы закрепить цену ↓",
        reply_markup=phone_kb,
    )
    await state.set_state(BizForm.phone)


@dp.message(F.contact, BizForm.phone)
async def biz_finish(m: Message, state: FSMContext):
    data = await state.get_data()
    save_lead(
        {
            "id": m.from_user.id,
            "first_name": m.from_user.first_name,
            "username": m.from_user.username or "",
            "phone": m.contact.phone_number,
        },
        source="business",
        payload=data,
    )
    await m.answer("✅ Спасибо! Мы свяжемся с вами в ближайшее время.", reply_markup=main_menu)
    await m.answer(
    "🗓 Забронируйте 30-мин консультацию по бизнес-setup:",
    reply_markup=kb_consult_biz
)
    await state.clear()


# ================= запуск =================
# ---------- мини-квиз «🗓 30-мин консультация» ----------
@dp.message(F.text == "🗓 30-мин консультация")
async def consult_start(m: Message, state: FSMContext):
    await m.answer("О какой теме хотите поговорить?", reply_markup=kb_consult_topic)
    await state.set_state(ConsultForm.topic)

@dp.message(ConsultForm.topic)
async def consult_topic(m: Message, state: FSMContext):
    await state.update_data(topic=m.text)
    await m.answer("Как вас зовут?")
    await state.set_state(ConsultForm.name)

@dp.message(ConsultForm.name)
async def consult_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("📧 Ваш e-mail:")
    await state.set_state(ConsultForm.email)

@dp.message(ConsultForm.email)
async def consult_email(m: Message, state: FSMContext):
    if not EMAIL_RE.match(m.text.strip()):
        return await m.answer("Введите корректный e-mail (пример user@example.com):")
    await state.update_data(email=m.text)
    await m.answer("📞 Нажмите «Поделиться телефоном»", reply_markup=phone_kb)
    await state.set_state(ConsultForm.phone)

@dp.message(F.contact, ConsultForm.phone)
async def consult_finish(m: Message, state: FSMContext):
    data = await state.get_data()
    save_lead(
        {"id": m.from_user.id,
         "first_name": m.from_user.first_name,
         "username": m.from_user.username or "",
         "phone": m.contact.phone_number},
        source="consult",
        payload=data,
    )

    topic = data["topic"].lower()
    if "недвиж" in topic:
        kb = kb_consult_estate
    else:
        kb = kb_consult_biz

    await m.answer(
        "🎉 Спасибо! Выберите удобное время по кнопке ниже:",
        reply_markup=kb
    )
    await state.clear()

@dp.message(ConsultForm.phone)
async def consult_phone_text(m: Message):
    await m.answer("Нажмите кнопку «📞 Поделиться телефоном» ниже.", reply_markup=phone_kb)
async def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())