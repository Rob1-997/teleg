from geopy.geocoders import Nominatim
import logging
from aiogram import F, Router, types
from aiogram.filters import CommandStart ,Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from database import add_user, upsert_profile,  is_admin, get_profile
from aiogram.types import BotCommandScopeChat

from io import BytesIO
import re
from utils.images import crop_square_bytes
import hendlers.keybords as kb
from utils.i18n import t , COMMANDS

router = Router()
geolocator = Nominatim(user_agent="my_bot_geocoder", timeout=10)
logger = logging.getLogger(__name__)




class Reg(StatesGroup):
    language = State()
    name = State()
    gender = State()
    age = State()
    location = State()
    numbers = State()
    photo = State()

# async def menu_for(user_id: int):
#     if await is_admin(user_id):
#         return kb.admin_menu
#     row = await get_profile(user_id)
#     lang = row["lang"] if row and row.get("lang") else "ru"

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):


    user_id = message.from_user.id
    profile = await get_profile(user_id)

    if profile and profile.get("name"):
        lang = profile.get("lang", "ru")
        # Устанавливаем команды именно для этого чата и этого пользователя
        await message.bot.set_my_commands(
            commands=COMMANDS[lang],
            scope=BotCommandScopeChat(chat_id=user_id)
        )

        text = t("welcome_back", lang, name=profile.get("name"))
        return await message.answer(text , parse_mode='HTML')

    # иначе — предложить выбрать язык
    await state.set_state(Reg.language)
    await message.answer(
        "👋 Select Language / Выберите язык / Ընտրեք լեզուն",
        reply_markup=kb.language_kb, parse_mode="HTML"
    )

# 3) Когда пользователь выбирает язык, тоже сохраняем его и сразу назначаем команды:
@router.message(Reg.language)
async def process_language_choice(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang    = msg.text  # ожидаем "ru", "en" или "am"

    # Сохраняем язык в БД (через upsert_profile или вашу функцию)
    await upsert_profile(user_id, lang=lang, )  # остальные поля можно передавать позже

    # Обновляем команды именно под этот чат
    await msg.bot.set_my_commands(
        commands=COMMANDS[lang],
        scope=BotCommandScopeChat(chat_id=user_id)
    )

    await state.clear()
    await msg.answer(
        t("reg_done", lang),
    )

# 4) При старте бота один раз включите иконку “/” слева у всех:


@router.callback_query(Reg.language, F.data.startswith("lang_"))
async def cmd_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_", 1)[1]
    await state.update_data(language=lang)

    await state.set_state(Reg.gender)
    await callback.message.edit_text(
        t("ask_gender", lang),
        reply_markup=kb.gender_kb(lang)
    )

@router.callback_query(Reg.gender, F.data == "male")
async def cmd_male(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await state.update_data(gender="male")
    await state.set_state(Reg.name)
    await callback.message.edit_text(t("ask_name", lang))

@router.callback_query(Reg.gender, F.data == "female")
async def cmd_female(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await state.update_data(gender="female")
    await state.set_state(Reg.name)
    await callback.message.edit_text(t("ask_name", lang))

@router.message(Reg.name, F.text)
async def save_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    text = message.text.strip()

    if text.isdigit() or len(text) < 2:
        return await message.answer(t("err_name_digit", lang), parse_mode="HTML")
    if not re.fullmatch(r"^[A-Za-zА-Яа-яЁёԱ-Ֆա-ֆ \-]+$", text):
        return await message.answer(t("err_name_format", lang), parse_mode="HTML")

    await state.update_data(name=text)
    await state.set_state(Reg.age)
    await message.answer(t("ask_age", lang, name=text) , parse_mode="HTML")

@router.message(Reg.name)
async def reject_non_text_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    return await message.answer(
        t("err_name_nontext", lang),parse_mode="HTML"
    )

@router.message(Reg.age, F.text)
async def on_age_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    text = message.text.strip()

    if not text.isdigit():
        return await message.answer(t("err_age_nondigit", lang) , parse_mode="HTML")
    age = int(text)
    if not 14 <= age <= 80:
        return await message.answer(t("err_age_range", lang) , parse_mode="HTML")

    await state.update_data(age=age)
    await state.set_state(Reg.location)
    await message.answer(
        t("ask_location", lang, step=4),
        reply_markup=kb.location_kb(lang) , parse_mode='HTML'
    )

@router.message(Reg.age, ~F.text)
async def on_age_non_text(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language", "ru")
    await message.answer(t("err_age_nontext", lang) , parse_mode="HTML")

@router.message(Reg.location, F.location)
async def handle_location_geo_reg(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    lat, lon = message.location.latitude, message.location.longitude

    try:
        place   = geolocator.reverse((lat, lon), language="en", zoom=10)
        address = place.raw.get("address", {})
        logger.info(f"Nominatim address for {lat},{lon}: {address}")

        raw_city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or ""
        ).strip()

        # Убираем «Border …» и всё после «-»
        if raw_city.lower().startswith("border "):
            raw_city = raw_city[len("Border "):].strip()
        if "-" in raw_city:
            raw_city = raw_city.split("-", 1)[0].strip()

        city = raw_city or None

    except Exception:
        logger.exception("Geocode reverse failed")
        city = None

    # Если не удалось получить город, сохраняем координаты
    text_loc = city or f"{lat:.6f},{lon:.6f}"

    # Сохраняем в state и переходим к фото
    await state.update_data(location=text_loc)
    await state.set_state(Reg.photo)

    # Ответ пользователю

    await message.answer(
        t("ask_photo", lang, step=6)
    )

@router.message(Reg.location, F.text)
async def handle_location_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    city = message.text.strip()

    # 1) Не цифры и длина минимум 2
    if city.isdigit() or len(city) < 2:
        return await message.answer(
            t("err_location_numeric", lang),
            reply_markup=kb.location_kb(lang) , parse_mode="HTML"
        )
    # 2) Только буквы (рус/англ/арм), пробелы и дефис
    if not re.fullmatch(r"[A-Za-zА-Яа-яЁёԱ-Ֆա-ֆ\s\-]+", city):
        return await message.answer(
            t("err_location_format", lang),
            reply_markup=kb.location_kb(lang) , parse_mode='HTML'
        )

    # Сохраняем текст города
    await state.update_data(location=city)
    await state.set_state(Reg.photo)

    # Убираем клавиатуру, шлём следующий prompt

    await message.answer(
        t("ask_photo", lang, step=6),
        reply_markup=ReplyKeyboardRemove() , parse_mode="HTML"
    )

@router.message(Reg.location, ~F.text, ~F.location)
async def reject_location_other(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await message.answer(
        t("err_location_other", lang),
        reply_markup=kb.location_kb(lang) , parse_mode="HTML"
    )

@router.message(Reg.photo)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")

    if not message.photo:
        return await message.answer(t("err_photo_not_image", lang) ,parse_mode="HTML")

    largest = message.photo[-1]
    file_obj = await message.bot.get_file(largest.file_id)
    buf = BytesIO()
    await message.bot.download_file(file_obj.file_path, destination=buf)
    raw_bytes = buf.getvalue()
    squared = await crop_square_bytes(raw_bytes, size=800)

    await state.update_data(photo_data=squared)
    await state.set_state(Reg.numbers)
    await message.answer(t("contact", lang), reply_markup=kb.contact_kb(lang))

@router.message(Reg.numbers, F.contact)
async def on_contact(message: Message, state: FSMContext):
    # 1) Получаем существующие данные
    data = await state.get_data()
    lang = data.get("language", "ru")

    contact = message.contact
    if contact.user_id != message.from_user.id:
        return await message.answer(t("err_contact_not_owner", lang), parse_mode="HTML")

    # 2) Сохраняем номер в стейт
    await state.update_data(numbers=contact.phone_number)

    # 3) Получаем уже обновлённый стейт
    data = await state.get_data()
    photo_bytes = data.get("photo_data")
    if not photo_bytes:
        return await message.answer(t("err_no_photo", lang))

    try:
        # 4) Если нужно, заводим запись в users
        await add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name
        )
        # 5) Сохраняем профиль в БД
        await upsert_profile(
            message.from_user.id,
            gender=data["gender"],
            name=data["name"],
            age=int(data["age"]),
            location=data["location"],
            phone=data["numbers"],
            photo_data=photo_bytes,
            lang=lang
        )
    except Exception as e:
        return await message.answer(t("save_profile_error", lang, error=str(e)))

    # 6) Отправляем итоговый профиль

    buf2 = BytesIO(photo_bytes)
    caption = t(
        "confirm_caption", lang,
        gender=data["gender"],
        name=data["name"],
        age=data["age"],
        location=data["location"],
    )
    await message.answer_photo(
        types.BufferedInputFile(buf2.getvalue(), filename="profile.jpg"),
        caption=caption,
        reply_markup=ReplyKeyboardRemove()
    )

    # 7) Завершаем стейт и показываем главное меню
    user_id = message.from_user.id
    await message.bot.set_my_commands(
        commands=COMMANDS[lang],
        scope=BotCommandScopeChat(chat_id=user_id)
    )
    await state.clear()
    await message.answer(
        t("reg_done", lang),
    )


@router.message(Reg.numbers, ~F.contact)
async def invalid_contact_format(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await message.answer(
        t("err_contact_not_owner", lang),
        reply_markup=kb.contact_kb(lang),
        parse_mode="HTML"
    )



