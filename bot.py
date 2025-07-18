# bot.py — clean build 2025-07-18 (полностью проверено)
import asyncio, logging, os, re
from pathlib import Path
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

# ── env ──────────────────────────────────────────────
load_dotenv(Path(__file__).with_name(".env"))
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN missing in .env")

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp  = Dispatcher()

# ── local imports ───────────────────────────────────
from keyboards import (
    main_menu, phone_kb, yes_no_kb, kb_company, kb_niche, kb_visas,
    kb_locations, kb_budget_estate, kb_consult_estate, kb_consult_biz,
    kb_consult_topic, kb_freezones, kb_plan_time,
    kb_estate_intro_inline, kb_biz_intro_inline, kb_youtube
)
from states  import EstateForm, BizForm, ConsultForm  # name-state обязателен
from texts   import WELCOME_TEXT, FREEZONE_VS_MAINLAND, GUIDE_BUSINESS, GUIDE_ESTATE
from utils   import calc_cost
from sheets  import save_lead

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# ══════════════ /start ══════════════
@dp.message(F.text == "/start")
async def cmd_start(m: Message, state: FSMContext):
    await m.answer(WELCOME_TEXT, reply_markup=main_menu)
    await state.clear()

# ══════════════ Недвижимость ══════════════
@dp.message(F.text == "🏠 Недвижимость")
async def estate_preview(m: Message, state: FSMContext):
    await m.answer(
        "Недвижимость в ОАЭ — один из самых прибыльных рынков мира.\n"
        "Нажмите «Начать», чтобы пройти квиз и получить PDF-гайд.",
        reply_markup=kb_estate_intro_inline)
    await state.clear()

@dp.callback_query(F.data == "start_estate")
async def estate_start_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await est_start(cb.message, state)

async def est_start(msg: Message, state: FSMContext):
    await msg.answer("Ваш бюджет:", reply_markup=kb_budget_estate)
    await state.set_state(EstateForm.budget)

@dp.message(EstateForm.budget)
async def est_budget(m: Message, state: FSMContext):
    await state.update_data(budget=m.text)
    await m.answer("Локация:", reply_markup=kb_locations)
    await state.set_state(EstateForm.location)

@dp.message(EstateForm.location)
async def est_location(m: Message, state: FSMContext):
    await state.update_data(location=m.text)
    await m.answer("Когда планируете инвестировать?", reply_markup=kb_plan_time)
    await state.set_state(EstateForm.plan_time)

@dp.message(EstateForm.plan_time)
async def est_plan_time(m: Message, state: FSMContext):
    await state.update_data(plan_time=m.text)
    await m.answer("Как к вам обращаться?")
    await state.set_state(EstateForm.name)

@dp.message(EstateForm.name)
async def est_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("📧 Ваш e-mail:")
    await state.set_state(EstateForm.email)

@dp.message(EstateForm.email)
async def est_email(m: Message, state: FSMContext):
    if not EMAIL_RE.match(m.text.strip()):
        return await m.answer("E-mail некорректен. Пример: user@mail.com")
    await state.update_data(email=m.text)
    await m.answer("📞 Нажмите «Поделиться телефоном»", reply_markup=phone_kb)
    await state.set_state(EstateForm.phone)

@dp.message(F.contact, EstateForm.phone)
async def est_finish(m: Message, state: FSMContext):
    data = await state.get_data()
    save_lead(
        {"id": m.from_user.id,
         "first_name": m.from_user.first_name,
         "username": m.from_user.username or "",
         "phone": m.contact.phone_number},
        source="estate", payload=data)
    await m.answer("📗 Бесплатный гайд:\n" + GUIDE_ESTATE)
    await m.answer("🎉 Спасибо! Мы свяжемся с вами в ближайшее время.",
                   reply_markup=main_menu)
    await m.answer("🗓 Записаться на 30-мин консультацию:",
                   reply_markup=kb_consult_estate)
    await m.answer("⬅️ Вернуться в главное меню", reply_markup=main_menu)
    await state.clear()

@dp.message(~F.contact, EstateForm.phone)
async def est_phone_retry(m: Message):
    await m.answer("Нажмите кнопку «📞 Поделиться телефоном».", reply_markup=phone_kb)

# ══════════════ Бизнес + калькулятор ══════════════
@dp.message(F.text == "🏢 Бизнес + Калькулятор")
async def biz_preview(m: Message, state: FSMContext):
    await m.answer(
        "Расчитайте стоимость лицензии и получите PDF «13 ошибок».\n"
        "Нажмите «Начать».",
        reply_markup=kb_biz_intro_inline)
    await state.clear()

@dp.callback_query(F.data == "start_biz")
async def biz_start_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await biz_quiz_start(cb.message, state)

async def biz_quiz_start(msg: Message, state: FSMContext):
    await msg.answer(FREEZONE_VS_MAINLAND)
    await msg.answer("Ниша бизнеса?", reply_markup=kb_niche)
    await state.set_state(BizForm.niche)

@dp.message(BizForm.niche)
async def biz_niche(m: Message, state: FSMContext):
    await state.update_data(niche=m.text)
    await m.answer(
        "🔍 <b>Free Zone</b> — 0 % налога, 100 % иностранное владение, только внутри зоны.\n"
        "🔍 <b>Mainland</b> — деятельность по всему ОАЭ, офис обязателен.\n\n"
        "<b>Какой тип компании?</b>",
        reply_markup=kb_company)
    await state.set_state(BizForm.company_type)

@dp.message(BizForm.company_type)
async def biz_type(m: Message, state: FSMContext):
    if "free" in m.text.lower():
        await state.update_data(company_type="FZ")
        await m.answer("Выберите Free-Zone:", reply_markup=kb_freezones)
        await state.set_state(BizForm.freezone)
    else:
        await state.update_data(company_type="ML")
        await m.answer("Учредители уже резиденты? (Да/Нет)", reply_markup=yes_no_kb)
        await state.set_state(BizForm.residents)

@dp.message(BizForm.freezone)
async def biz_freezone(m: Message, state: FSMContext):
    await state.update_data(freezone=m.text)
    await m.answer("Учредители уже резиденты? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.residents)

@dp.message(BizForm.residents)
async def biz_residents(m: Message, state: FSMContext):
    await state.update_data(residents=m.text.lower() == "да")
    await m.answer("Сколько виз нужно?", reply_markup=kb_visas)
    await state.set_state(BizForm.visas)

@dp.callback_query(F.data.startswith("vis_"), BizForm.visas)
async def biz_visas_cb(cb: CallbackQuery, state: FSMContext):
    await state.update_data(visas=int(cb.data.split("_")[1]))
    await cb.message.edit_reply_markup()
    await cb.message.answer("Нужен офис? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.office)
    await cb.answer()

@dp.message(BizForm.visas)
async def biz_visas_text(m: Message, state: FSMContext):
    if m.text.isdigit() and 0 <= int(m.text) <= 10:
        await state.update_data(visas=int(m.text))
        await m.answer("Нужен офис? (Да/Нет)", reply_markup=yes_no_kb)
        await state.set_state(BizForm.office)
    else:
        await m.answer("Введите число 0-10 или нажмите кнопку.")

@dp.message(BizForm.office)
async def biz_office(m: Message, state: FSMContext):
    await state.update_data(office=m.text.lower() == "да")
    await m.answer("Нужен корпоративный счёт? (Да/Нет)", reply_markup=yes_no_kb)
    await state.set_state(BizForm.bank)

@dp.message(BizForm.bank)
async def biz_bank(m: Message, state: FSMContext):
    await state.update_data(bank=m.text.lower() == "да")
    await m.answer("Когда планируете открыть бизнес?", reply_markup=kb_plan_time)
    await state.set_state(BizForm.plan_time)

@dp.message(BizForm.plan_time)
async def biz_plan_time(m: Message, state: FSMContext):
    await state.update_data(plan_time=m.text)
    await m.answer("Как к вам обращаться?")
    await state.set_state(BizForm.name)

@dp.message(BizForm.name)
async def biz_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("📧 Ваш e-mail:")
    await state.set_state(BizForm.email)

@dp.message(BizForm.email)
async def biz_email(m: Message, state: FSMContext):
    if not EMAIL_RE.match(m.text.strip()):
        return await m.answer("E-mail некорректен. Пример: founder@mail.com")
    await state.update_data(email=m.text)
    await m.answer("📞 Нажмите «Поделиться телефоном»", reply_markup=phone_kb)
    await state.set_state(BizForm.phone)

@dp.message(F.contact, BizForm.phone)
async def biz_finish(m: Message, state: FSMContext):
    data = await state.get_data()
    total = calc_cost(data)
    save_lead(
        {"id": m.from_user.id,
         "first_name": m.from_user.first_name,
         "username": m.from_user.username or "",
         "phone": m.contact.phone_number},
        source="business", payload=data)
    await m.answer(f"💸 Стоимость регистрации <b>от AED {total:,}</b>")
    await m.answer("📘 Гайд «13 ошибок в бизнесе»:\n" + GUIDE_BUSINESS)
    await m.answer("🗓 Записаться на 30-мин консультацию:",
                   reply_markup=kb_consult_biz)
    # Кнопка возврата в главное меню
    await m.answer("⬅️ Вернуться в главное меню", reply_markup=main_menu)
    await state.clear()

@dp.message(~F.contact, BizForm.phone)
async def biz_phone_retry(m: Message):
    await m.answer("Нажмите «📞 Поделиться телефоном».", reply_markup=phone_kb)

# ══════════════ Консультация ══════════════
@dp.message(F.text == "🗓 Консультация")
async def consult_entry(m: Message, state: FSMContext):
    await m.answer("О какой теме хотите поговорить? (Недвижимость / Бизнес)",
                   reply_markup=kb_consult_topic)
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
        return await m.answer("E-mail некорректен. Пример: user@mail.com")
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
        source="consult", payload=data)
    kb = kb_consult_estate if "недвиж" in data["topic"].lower() else kb_consult_biz
    await m.answer("🎉 Спасибо! Выберите удобное время:", reply_markup=kb)
    await m.answer("⬅️ Вернуться в главное меню", reply_markup=main_menu)
    await state.clear()

@dp.message(~F.contact, ConsultForm.phone)
async def consult_phone_retry(m: Message):
    await m.answer("Нажмите «📞 Поделиться телефоном».", reply_markup=phone_kb)

# ══════════════ Полезное видео ══════════════
@dp.message(F.text == "🎬 Полезная кнопка")
async def useful_links(m: Message, state: FSMContext):
    await m.answer("Полезные видео о рынке ОАЭ 👇", reply_markup=kb_youtube)

# ── main ───────────────────────────────────
async def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())