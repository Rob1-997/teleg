from unidecode import unidecode
from geopy.geocoders import Nominatim
from aiogram.filters import Command

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery , ReplyKeyboardRemove
from database import get_profile, update_profile_field , clear_dialog , get_partner
from io import BytesIO
from utils.images import crop_square_bytes
import re                    # ← вот это
import hendlers.keybords as kb
from utils.i18n import t



from hendlers.hendler import cmd_start
from hendlers.search import cmd_search
from hendlers.blocks import cmd_block_list
from hendlers.language import cmd_set_language

router = Router()
geolocator = Nominatim(user_agent="my_bot_geocoder", timeout=10)
logger = logging.getLogger(__name__)

class Edit(StatesGroup):
    name     = State()
    age      = State()
    location = State()
    photo    = State()


@router.message(Command("cancel_edit"))
async def cancel_edit_cmd(msg: Message, state: FSMContext):
    row = await get_profile(msg.from_user.id)
    lang = row.get("lang") or "ru"
    await state.clear()
    await msg.answer(t('answer_cancelled' , lang), reply_markup=ReplyKeyboardRemove())



# -------- показать профиль --------
@router.message(Command("profile"))
async def cmd_profile(msg: Message, state: FSMContext):
    await state.clear()
    row = await get_profile(msg.from_user.id)
    if not row:
        return await msg.answer(
            t("err_not_registered", "ru"),
            reply_markup=kb.not_registration_kb("ru")
        )

    lang = row["lang"]
    caption = t(
        "profile_caption", lang,
        gender   = row["gender"],
        name     = row["name"],
        age      = row["age"],
        location = row["location"],
        phone    = row["phone"],
    )

    buffer = BytesIO(row["photo_data"])
    await msg.answer_photo(
        types.BufferedInputFile(buffer.getvalue(), filename="profile.jpg"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb.edit_entry_kb(lang) ,
    )

@router.callback_query(F.data == "edit_menu")
async def open_edit_menu(cb: CallbackQuery):
    # 1) Берём язык пользователя из БД
    row  = await get_profile(cb.from_user.id)
    lang = row.get("lang") or "ru"

    # 2) Генерируем клавиатуру действий по профилю на нужном языке
    keyboard = kb.profile_actions_kb(lang)

    # 3) Обновляем разметку в том же сообщении
    await cb.message.edit_reply_markup(reply_markup=keyboard)
    await cb.answer()

# -------- выбор действия --------
@router.callback_query(F.data.startswith("edit_"))
async def edit_switch(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    row     = await get_profile(user_id)
    lang    = row.get("lang") or "ru"
    action  = cb.data.split("_", 1)[1]

    await cb.answer()  # закрываем «часики»

    if action == "name":
        await cb.message.answer(t("edit_name_prompt", lang) , parse_mode="HTML" , )
        await state.set_state(Edit.name)

    elif action == "age":
        await cb.message.answer(t("edit_age_prompt", lang) , parse_mode="HTML")
        await state.set_state(Edit.age)

    elif action == "city":
        await cb.message.answer(
            t("edit_city_prompt", lang),
            reply_markup=kb.location_kb(lang) , parse_mode="HTML"
        )
        await state.set_state(Edit.location)

    elif action == "photo":
        await cb.message.answer(t("edit_photo_prompt", lang) , parse_mode="HTML")
        await state.set_state(Edit.photo)

# -------- обработка имени --------
@router.message(Edit.name, F.text)
async def save_new_name(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    row     = await get_profile(user_id)
    lang    = row.get("lang") or "ru"
    name    = msg.text.strip()


    if msg.text == "/start":

        await state.clear()
        return await cmd_start(msg, state)

    elif msg.text == "/profile":
        await state.clear()
        return await cmd_profile(msg, state)

    elif msg.text == "/search":
        await state.clear()
        return await cmd_search(msg, state)

    elif msg.text == "/block_list":
        await state.clear()
        return await cmd_block_list(msg)

    elif msg.text == "/language":
        await state.clear()
        return await cmd_set_language(msg, state)

    # 1) Проверяем — не цифры и не слишком короткое
    if name.isdigit() or len(name) <= 3:
        return await msg.answer(
            t("err_edit_name_invalid", lang),parse_mode="HTML"
        )

    # 2) Проверяем формат — только буквы, пробел или дефис
    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]+", name):
        return await msg.answer(
            t("err_edit_name_invalid", lang),parse_mode="HTML"
        )


    # 3) Всё ок — сохраняем
    await update_profile_field(user_id, "name", name)
    await state.clear()

    # 4) Подтверждаем и показываем главное меню на нужном языке
    await msg.answer(
        t("edit_name_success", lang),
    )

# 2) Ловим всё остальное (фото, файл, стикер и т.п.) и отказываем
@router.message(Edit.name, ~F.text)
async def reject_non_text_name(msg: Message):
    user_id = msg.from_user.id
    row     = await get_profile(user_id)
    lang    = row.get("lang") or "ru"

    await msg.answer(
        t("err_edit_name_invalid", lang),parse_mode="HTML"
    )


# -------- обработка возраста --------
@router.message(Edit.age, F.text)
async def save_new_age_text(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    row     = await get_profile(user_id)
    lang    = row.get("lang") or "ru"
    text    = msg.text.strip()

    if msg.text == "/start":
        await state.clear()
        return await cmd_start(msg, state)

    elif msg.text == "/profile":
        await state.clear()
        return await cmd_profile(msg, state)

    elif msg.text == "/search":
        await state.clear()
        return await cmd_search(msg, state)

    elif msg.text == "/block_list":
        await state.clear()
        return await cmd_block_list(msg)

    elif msg.text == "/language":
        await state.clear()
        return await cmd_set_language(msg, state)


    # Только цифры 10–99
    if not text.isdigit():
        return await msg.answer(t("err_edit_age_nondigit", lang),parse_mode="HTML")
    age = int(text)
    if not 14 <= age <= 80:
        return await msg.answer(t("err_edit_age_range", lang),parse_mode="HTML")

    # Сохраняем и выходим из FSM
    await update_profile_field(user_id, "age", age)
    await state.clear()
    await msg.answer(
        t("edit_age_success", lang),
    )

@router.message(Edit.age, ~F.text)
async def reject_non_text_age(msg: Message):
    user_id = msg.from_user.id
    row     = await get_profile(user_id)
    lang    = row.get("lang") or "ru"

    # Если прислали не текст
    await msg.answer(t("err_edit_age_nondigit", lang),parse_mode="HTML")


# -------- обработка города --------

@router.message(Edit.location, F.location)
async def edit_location_geo(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    prof    = await get_profile(user_id)
    lang    = prof.get("lang") or "ru"
    lat, lon = msg.location.latitude, msg.location.longitude
    print("10")

    try:
        place   = geolocator.reverse((lat, lon), language="en", zoom=10)
        address = place.raw.get("address", {})
        logger.info(f"Nominatim address for {lat},{lon}: {address}")

        # выбираем «город»
        raw_city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or ""
        ).strip()

        # если Nominatim вернул «Border …», обрезаем префикс и всё после «-»
        if raw_city.lower().startswith("border "):
            raw_city = raw_city[len("Border "):]
        if "-" in raw_city:
            raw_city = raw_city.split("-", 1)[0].strip()

        city = raw_city or None

    except Exception:
        logger.exception("Geocode reverse failed")
        city = None

    # если всё ещё нет нормального названия — падаем на координаты
    text_loc = city or f"{lat:.6f},{lon:.6f}"

    await update_profile_field(user_id, "location", text_loc)

    await state.clear()
    await msg.answer(
        t("edit_city_geo_success", lang),
    )

# 2) Иначе, если пришёл текст — валидируем как название города
@router.message(Edit.location, F.text)
async def edit_location_text(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    prof    = await get_profile(user_id)
    lang    = prof.get("lang") or "ru"
    city    = msg.text.strip()
    if msg.text == "/start":

        await msg.answer(t("btn_cancel", lang), parse_mode="HTML")
        await state.clear()
        return await cmd_start(msg, state)
    elif msg.text == "/profile":
        await msg.answer(t("btn_cancel", lang), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return await cmd_profile(msg, state)
    elif msg.text == "/search":
        await msg.answer(t("btn_cancel", lang),parse_mode="HTML" , reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return await cmd_search(msg, state)
    elif msg.text == "/block_list":
        await msg.answer(t("btn_cancel", lang), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return await cmd_block_list(msg)
    elif msg.text == "/language":
        await msg.answer(t("btn_cancel", lang), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return await cmd_set_language(msg, state)
    # Ваша валидация: минимум 2 символа и только буквы, пробел, дефис
    if city.isdigit() or len(city) <= 2:
        return await msg.answer(
            t("err_edit_city_numeric", lang),
            reply_markup=kb.location_kb(lang) , parse_mode="HTML"
        )
    if not re.fullmatch(r"[A-Za-zА-Яа-яЁёԱ-Ֆա-ֆ\s\-]+", city):
        return await msg.answer(
            t("err_edit_city_format", lang),
            reply_markup=kb.location_kb(lang)
        )

    # Здесь транслитерируем введённый город:
    city_latin = unidecode(city)

    await update_profile_field(user_id, "location", city_latin)
    await state.clear()
    await msg.answer(
        t("edit_city_success", lang) , reply_markup=ReplyKeyboardRemove()
    )

# 3) Всё остальное — просим прислать текст или гео
@router.message(Edit.location, ~F.text, ~F.location)
async def edit_location_other(msg: Message,state: FSMContext):

    prof = await get_profile(msg.from_user.id)
    lang = prof.get("lang") or "ru"

    await msg.answer(
        t("err_edit_city_other", lang),
        reply_markup=kb.location_kb(lang)
    )

# -------- обработка фотографии --------
@router.message(Edit.photo, F.photo)
async def save_new_photo(msg: Message, state: FSMContext):

    # Скачиваем байты
    largest = msg.photo[-1]
    file_obj = await msg.bot.get_file(largest.file_id)
    buf = BytesIO()
    await msg.bot.download_file(file_obj.file_path, destination=buf)
    raw = buf.getvalue()

    # Обрезаем и меняем размер
    squared = await crop_square_bytes(raw, size=320)

    # Сохраняем в БД
    await update_profile_field(msg.from_user.id, "photo_data", squared)
    await state.clear()
    user_id = msg.from_user.id
    row = await get_profile(user_id)
    lang = row.get("lang") or "ru"
    # Отправляем пользователю новое фото
    buf2 = BytesIO(squared)
    await msg.answer_photo(
        types.BufferedInputFile(buf2.getvalue(), filename="updated_photo.jpg"),
        caption=t('edit_photo_success' , lang),
    )

# 2) Любой другой контент — отказ
@router.message(Edit.photo, ~F.photo)
async def reject_non_photo(msg: Message , state: FSMContext):
    user_id = msg.from_user.id
    row     = await get_profile(user_id)
    lang    = row.get("lang") or "ru"
    if msg.text == "/start":
        await state.clear()
        return await cmd_start(msg, state)

    elif msg.text == "/profile":
        await state.clear()
        return await cmd_profile(msg, state)

    elif msg.text == "/search":
        await state.clear()
        return await cmd_search(msg, state)

    elif msg.text == "/block_list":
        await state.clear()
        return await cmd_block_list(msg)

    elif msg.text == "/language":
        await state.clear()
        return await cmd_set_language(msg, state)

    await msg.answer(
        t("err_edit_photo_invalid", lang),parse_mode="HTML"
    )


