import asyncio
import json
from pathlib import Path
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.client.default import DefaultBotProperties

# ===== Настройки =====
BOT_TOKEN = "8213766383:AAFsspze3t60GQ12pPpgxL-SMK4g5ylxZT0"  # <-- сюда вставь токен своего DATA_FILE = Path("bookings.json")
STUDIO_NAME = "🖤 Tattoo Studio Люции"
STUDIO_ADDRESS = "📍 Гурьбы 96, салон Татьяна"
STUDIO_CONTACT = "+7 771 284 08 06"
# ======================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# === Машина состояний ===
class BookingForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    time = State()
    place_on_body = State()
    size = State()
    description = State()
    photo = State()
    confirm = State()

# === Утилиты ===
def load_bookings():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_booking(booking: dict):
    bookings = load_bookings()
    bookings.append(booking)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)

def update_booking_status(user_id: int, status: str):
    bookings = load_bookings()
    for b in bookings:
        if b["user_id"] == user_id and b.get("status") == "ожидание":
            b["status"] = status
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(bookings, f, ensure_ascii=False, indent=2)
            return b
    return None

# === Клавиатуры ===
def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Записаться на тату")],
            [KeyboardButton(text="💬 Частые вопросы"), KeyboardButton(text="📸 Портфолио")],
            [KeyboardButton(text="📞 Контакты")]
        ],
        resize_keyboard=True
    )

def back_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
        resize_keyboard=True
    )

# === Старт ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        f"👋 Привет, {message.from_user.first_name or 'друг'}!\n\n"
        f"Добро пожаловать в <b>{STUDIO_NAME}</b> 💎\n"
        f"Здесь можно записаться, узнать стоимость и вдохновиться.\n\n"
        f"Выбери действие 👇"
    )
    await message.answer_photo(
        photo="https://i.imgur.com/5KfT8QG.jpeg",  # <--- сюда можешь вставить свою картинку
        caption=text,
        reply_markup=main_menu_kb()
    )

# === Главное меню ===
@dp.message(F.text.in_(["📅 Записаться на тату", "💬 Частые вопросы", "📸 Портфолио", "📞 Контакты", "🏠 Главное меню"]))
async def main_menu(message: types.Message, state: FSMContext):
    if message.text == "📅 Записаться на тату":
        await message.answer("Как вас зовут?", reply_markup=back_main_kb())
        await state.set_state(BookingForm.name)
    elif message.text == "💬 Частые вопросы":
        await message.answer("💬 Задайте свой вопрос мастеру:", reply_markup=back_main_kb())
    elif message.text == "📸 Портфолио":
        await message.answer("Наш Instagram: <b>@colnyshko</b> и <b>@tattoo_studio_222</b> 💉", reply_markup=main_menu_kb())
    elif message.text == "📞 Контакты":
        await message.answer(f"{STUDIO_ADDRESS}\n📞 <b>{STUDIO_CONTACT}</b>", reply_markup=main_menu_kb())
    elif message.text == "🏠 Главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu_kb())

# === Запись шаги ===
@dp.message(BookingForm.name)
async def step_name(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu_kb())
        return
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона:", reply_markup=back_main_kb())
    await state.set_state(BookingForm.phone)

@dp.message(BookingForm.phone)
async def step_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Выберите дату 🗓", reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(BookingForm.date)

@dp.callback_query(SimpleCalendarCallback.filter())
async def step_date(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        await state.update_data(date=date.strftime("%d.%m.%Y"))
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="11:00"), KeyboardButton(text="13:00")],
                [KeyboardButton(text="15:00"), KeyboardButton(text="17:00")],
                [KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )
        await bot.send_message(callback.from_user.id, f"Вы выбрали <b>{date.strftime('%d.%m.%Y')}</b>\nТеперь выберите время:", reply_markup=kb)
        await state.set_state(BookingForm.time)

@dp.message(BookingForm.time)
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рука"), KeyboardButton(text="Нога")],
            [KeyboardButton(text="Плечо"), KeyboardButton(text="Спина")],
            [KeyboardButton(text="Шея"), KeyboardButton(text="Другое")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите место на теле для тату 💉:", reply_markup=kb)
    await state.set_state(BookingForm.place_on_body)

@dp.message(BookingForm.place_on_body)
async def step_place(message: types.Message, state: FSMContext):
    await state.update_data(place_on_body=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Маленькая (до 5 см)"), KeyboardButton(text="Средняя (5–15 см)")],
            [KeyboardButton(text="Большая (от 15 см)"), KeyboardButton(text="Не знаю")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Укажите примерный размер тату 📏:", reply_markup=kb)
    await state.set_state(BookingForm.size)

@dp.message(BookingForm.size)
async def step_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("Опишите идею или текст тату 🎨:", reply_markup=back_main_kb())
    await state.set_state(BookingForm.description)

@dp.message(BookingForm.description)
async def step_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Если хотите, отправьте фото/эскиз тату 📸 или напишите 'нет'", reply_markup=back_main_kb())
    await state.set_state(BookingForm.photo)

@dp.message(BookingForm.photo, F.photo)
async def step_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    await confirm_booking(message, state)

@dp.message(BookingForm.photo)
async def step_no_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=None)
    await confirm_booking(message, state)

async def confirm_booking(message: types.Message, state: FSMContext):
    data = await state.get_data()
    summary = (
        f"<b>Проверьте данные:</b>\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"📅 Дата: {data['date']} {data['time']}\n"
        f"📍 Место: {data['place_on_body']}\n"
        f"📏 Размер: {data['size']}\n"
        f"🎨 Идея: {data['description']}\n\n"
        "Подтверждаете запись? (Да / Нет)"
    )
    await message.answer(summary)
    await state.set_state(BookingForm.confirm)

@dp.message(BookingForm.confirm)
async def step_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() in ["да", "ок", "yes"]:
        data = await state.get_data()
        booking = {
            "user_id": message.from_user.id,
            "name": data["name"],
            "phone": data["phone"],
            "date": f"{data['date']} {data['time']}",
            "place_on_body": data["place_on_body"],
            "size": data["size"],
            "description": data["description"],
            "status": "ожидание",
            "created_at": datetime.now().isoformat()
        }
        save_booking(booking)

        await message.answer("✅ Заявка отправлена мастеру!", reply_markup=main_menu_kb())

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{message.from_user.id}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}")
                ]
            ]
        )

        msg_text = (
            f"📢 Новая запись:\n"
            f"👤 Имя: {booking['name']}\n"
            f"📱 Телефон: {booking['phone']}\n"
            f"📅 {booking['date']}\n"
            f"📍 {booking['place_on_body']}\n"
            f"📏 {booking['size']}\n"
            f"🎨 {booking['description']}"
        )

        if data.get("photo"):
            await bot.send_photo(ADMIN_CHAT_ID, data["photo"], caption=msg_text, reply_markup=kb)
        else:
            await bot.send_message(ADMIN_CHAT_ID, msg_text, reply_markup=kb)

        await state.clear()
    else:
        await message.answer("❌ Запись отменена.", reply_markup=main_menu_kb())
        await state.clear()

# === Ответ мастера ===
@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    booking = update_booking_status(user_id, "принята")
    if booking:
        await bot.send_message(user_id, "✅ Ваша запись подтверждена! До встречи 🖤")
        await callback.message.edit_text(f"✅ Запись {booking['name']} подтверждена.")
    else:
        await callback.answer("Ошибка при обновлении.")

@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    booking = update_booking_status(user_id, "отклонена")
    if booking:
        await bot.send_message(user_id, "❌ Время недоступно. Мастер свяжется для уточнения 🙏")
        await callback.message.edit_text(f"❌ Запись {booking['name']} отклонена.")
    else:
        await callback.answer("Ошибка при обновлении.")

# === Запуск ===
async def main():
    print("🤖 Бот работает и ждёт клиентов...")
    me = await bot.get_me()
    print(f"✅ Подключён как: {me.username}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ Бот остановлен.")
