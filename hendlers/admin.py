import os
import html
from aiogram import Router, F, types
from aiogram.types import Message ,CallbackQuery , InlineKeyboardButton , InlineKeyboardMarkup , BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from utils.i18n import t
from database import (
        set_admin, is_admin, search_profiles_by_name , get_profile_counts, get_all_users ,get_profile,
        get_online_count , ban, unban, get_all_bans ,get_messages_between , get_pairs , is_banned ,get_display_name)

import hendlers.keybords as kb
from collections import defaultdict
media_cache: dict[int, list[tuple[str, str, str | None]]] = defaultdict(list)

router = Router()

PASS = os.getenv("ADMIN_PASSWORD", )
ADMIN_ID = int(os.getenv("ADMIN_ID", ))

# ——— FSM: ждём пароль ———
class Auth(StatesGroup):
    wait_pass = State()

class Cast(StatesGroup):
    wait_text    = State()   # ждём текст объявления
    wait_confirm = State()


class SearchUsers(StatesGroup):
    wait_name = State()
    viewing   = State()

def admin_only(handler):
    async def wrapper(event, *a, **kw):
        if await is_admin(event.from_user.id):
            return await handler(event, *a, **kw)
        await event.answer("⛔ Только для админа.")
    return wrapper

async def safe_edit_text(message, text, **kwargs):
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        # иногда e.args = () → проверяем длину
        if len(e.args) == 0 or "message is not modified" in e.args[0]:
            return
        # иначе пробуем отправить как новое сообщение
        await message.answer(text, **kwargs)

# ——— команда/слово «admin» ———
@router.message(F.text.casefold() == "admin")
async def ask_pass(msg: types.Message, state: FSMContext):
    # хозяин без пароля
    if msg.from_user.id == ADMIN_ID:
        await set_admin(msg.from_user.id, True)
        return await msg.answer("🛠 Режим админа включён.", reply_markup=kb.admin_menu)

    await state.set_state(Auth.wait_pass)
    await msg.answer(
        f"Ваш ID: <code>{msg.from_user.id}</code>\n"
        f"Введите пароль для входа в админ-панель:",
        parse_mode="HTML"
    )

@router.message(F.text == "/answer_cancel")
async def cancel(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    row = await get_profile(user_id)
    lang = row.get("lang") or "ru"
    await state.clear()
    await msg.answer(t('btn_cancel' , lang))


@router.message(Auth.wait_pass)
async def check_pass(msg: types.Message, state: FSMContext):
    if msg.text == PASS:
        await set_admin(msg.from_user.id, True)
        await state.clear()
        return await msg.answer("✅ Пароль верный. Админ-меню доступно.", reply_markup=kb.admin_menu)
    await msg.answer("❌ Неверный пароль. Повторите или напишите /cancel.")

# ——— фильтр, который пускает только админов ———


# ——— /stats ———
@router.message(F.text == "📊 Статистика")
@admin_only
async def stats(msg: types.Message, **_):
    total, male, female = await get_profile_counts()
    await msg.answer(f"Всего: {total}\nПарни: {male}\nДевушки: {female}")

# ——— /send рассылка (очень упрощённая) ———


@router.message(F.text == "📨 Рассылка")
@admin_only
async def ask_bcast(msg: types.Message, state: FSMContext, **_):
    await state.set_state(Cast.wait_text)
    await msg.answer(
        "Пришлите текст рассылки.\n\n"
        "Нажмите «❌ Отмена», чтобы выйти.",
        reply_markup=kb.bcast_cancel_kb     # кнопка «Отмена»
    )

@router.message(Cast.wait_text, F.text)
async def preview_bcast(msg: types.Message, state: FSMContext):
    # если админ передумал и нажал кнопку меню → считаем это отменой
    if msg.text in {"👤 Профиль", "📊 Статистика", "🟢 Онлайн 24 ч",
                    "⬇️ Экспорт CSV", "🔍 Поиск", "🚫 Блок-лист",
                    "🚫 Бан-лист", "❌ Отмена", "🔙 Выйти из админки"}:
        await state.clear()
        return await msg.answer("Рассылка отменена.", reply_markup=kb.admin_menu)

    await state.update_data(text=msg.text)
    await state.set_state(Cast.wait_confirm)

    await msg.answer(
        f"❗️ <b>ПРЕВЬЮ рассылки</b> ❗️\n\n{msg.text}",
        parse_mode="HTML",
        reply_markup=kb.bcast_confirm_kb()   # ✅ / ❌
    )

@router.callback_query(F.data == "bcast_cancel", Cast.wait_confirm)
@admin_only
async def cancel_bcast(cb: CallbackQuery, state: FSMContext, **_):   # ← добавили **_
    await state.clear()

    # (1) меняем текст без inline-кнопок
    await cb.message.edit_text("Рассылка отменена.")

    # (2) выдаём правильное меню
    await cb.message.answer(
        "Главное меню",
        reply_markup=await kb.menu_for(cb.from_user.id)
    )
    await cb.answer("Отменено")


@router.callback_query(F.data == "bcast_send", Cast.wait_confirm)
@admin_only
async def do_cast(cb: CallbackQuery, state: FSMContext, **_):
    data = await state.get_data()
    text = data["text"]
    await state.clear()

    users = await get_all_users()      # [(id, name), ...]
    ok = err = 0
    for uid, _ in users:
        try:
            await cb.bot.send_message(uid, text)
            ok += 1
        except: err += 1

    await cb.message.edit_text(
        f"✅ Рассылка завершена.\n"
        f"Доставлено: <b>{ok}</b>\nОшибок: <b>{err}</b>",
        parse_mode="HTML"
    )
    await cb.message.answer(
        "Главное меню",
        reply_markup=await kb.menu_for(cb.from_user.id)
    )
    await cb.answer("Отправлено ✅")



@router.message(F.text.in_({"/logout", "🔙 Выйти из админки"}))
async def logout_cmd(msg: types.Message):
    await set_admin(msg.from_user.id, False)          # снимаем флаг
    await msg.answer(
        "Режим админа выключен.",
        reply_markup=await kb.menu_for(msg.from_user.id) # вернём нужное меню
    )
@router.message(F.text == "⬇️ Экспорт CSV")
@admin_only
async def export_csv(msg: types.Message, **_):
    import csv, io

    rows = await get_all_users()          # [(id, name), ...]
    if not rows:
        return await msg.answer("В базе пока нет пользователей.")

    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    buf.seek(0)

    await msg.answer_document(
        types.BufferedInputFile(buf.read().encode(),
                                filename="users.csv"),
        caption="Экспорт аудитории"
    )


@router.message(F.text == "🟢 Онлайн 24 ч")
@admin_only
async def online_now(msg: types.Message, **_):
    n = await get_online_count(24)
    await msg.answer(f"За последние 24 ч бота открывали: <b>{n}</b>", parse_mode="HTML")

@router.callback_query(F.data.regexp(r"^admin_ban_\d+$"))
@admin_only
async def cb_ban(cb: CallbackQuery, **_):
    uid = int(cb.data.split("_")[2])
    await ban(uid)
    await cb.answer("Забанен 🚫")
    await cb.message.edit_reply_markup(
        reply_markup=kb.admin_profile_kb(uid, True)
    )

@router.callback_query(F.data.regexp(r"^admin_unban_\d+$"))
@admin_only
async def cb_unban(cb: CallbackQuery, **_):
    uid = int(cb.data.split("_")[2])
    await unban(uid)
    await cb.answer("Разбанен ✅")
    await cb.message.edit_reply_markup(
        reply_markup=kb.admin_profile_kb(uid, False)
    )

# --- Кнопка «🚫 Бан-лист» -----------------------
@router.message(F.text == "🚫 Бан-лист")
@admin_only
async def show_ban_list(msg: types.Message, **_):
    rows = await get_all_bans()
    if not rows:
        return await msg.answer("Активных банов нет.", reply_markup=kb.admin_menu)

    users = []
    for r in rows:
        uid = r["telegram_id"]
        # берём из r["name"], если есть, иначе просто ID
        name = r.get("name") or r.get("full_name") or str(uid)
        users.append((uid, name))

    await msg.answer(
        "Заблокированные пользователи:",
        reply_markup=kb.bans_list_kb(users)
    )

@router.callback_query(F.data.regexp(r"^admin_unban_\d+$"))
@admin_only
async def unban_from_list(cb: CallbackQuery):
    uid = int(cb.data.split("_")[2])
    await unban(uid)

    rows = await get_all_bans()
    if not rows:
        # уходим в главное меню
        await cb.message.edit_text("Список банов пуст.", reply_markup=kb.admin_menu)
    else:
        users = [
            (r["telegram_id"], r["display_name"] or str(r["telegram_id"]))
            for r in rows
        ]
        # обновляем только клавиатуру
        await cb.message.edit_reply_markup(reply_markup=kb.bans_list_kb(users))

    await cb.answer("Разбанен ✅")


# 1) вывод списка диалогов
@router.message(F.text == "👀 Переписки")
@admin_only
async def show_pairs(msg: types.Message, **_):   #  ←  ОБЯЗАТЕЛЬНО  **_
    pairs = await get_pairs()
    await msg.answer(
        "Список диалогов (пары):",
        reply_markup=kb.dialog_pairs_kb(pairs)
    )

# 2) Просмотреть конкретного пользователя
@router.callback_query(F.data.regexp(r"^admin_pair_(\d+)_(\d+)$"))
@admin_only
async def show_pair_dialog(cb: CallbackQuery, **_):
    u1, u2 = map(int, cb.data.split("_")[2:])
    rows   = await get_messages_between(u1, u2, 50)

    media_cache[cb.from_user.id].clear()
    lines: list[str] = []
    buttons_row: list[InlineKeyboardButton] = []


    for r in reversed(rows):
        mark = "🟢" if r["sender_id"] == u1 else "⚪"
        ts   = r["sent_at"].strftime("%Y-%m-%d %H:%M")
        name = await get_display_name(r["sender_id"]) or r["sender_id"]

        safe_body = html.escape(r.get("body", ""), quote=False)
        ft, fid  = r.get("file_type"), r.get("file_id")

        if ft and fid:
            idx = len(media_cache[cb.from_user.id]) + 1
            media_cache[cb.from_user.id].append((ft, fid, safe_body or None))

            icon = "📎"
            buttons_row.append(
                InlineKeyboardButton(text=f"{icon}{idx}", callback_data=f"admin_media_{idx}")
            )
            body = f"[{ft} #{idx}] {safe_body}".strip()
        else:
            body = safe_body

        lines.append(f"{mark} {ts} — {name}: {body}")

    text = "\n".join(lines) or "Сообщений нет."

    kb_pairs = kb.dialog_pairs_kb(
        users=await get_pairs(),
        media_buttons=buttons_row,
        offset=0
    )

    await safe_edit_text(
        cb.message,
        f"Диалог <b>{u1}</b> ↔ <b>{u2}</b>\n\n{text}",
        parse_mode="HTML",
        reply_markup=kb_pairs
    )
    await cb.answer()


@router.callback_query(F.data.regexp(r"^admin_media_nav_(\d+)$"))
@admin_only
async def media_nav(cb: CallbackQuery, **_):
    offset = int(cb.data.rsplit("_", 1)[1])
    user_id = cb.from_user.id

    # Вызовите тот же код, что в show_pair_dialog, чтобы
    # media_cache[user_id] уже был заполнен полным списком:
    all_media_buttons = [
        InlineKeyboardButton(text=f"📎{i+1}", callback_data=f"admin_media_{i+1}")
        for i in range(len(media_cache[user_id]))
    ]

    # Перестроим клавиатуру с новым offset
    pairs = await get_pairs()
    kb_page = kb.dialog_pairs_kb(
        users=pairs,
        media_buttons=all_media_buttons,
        offset=offset
    )

    await cb.message.edit_reply_markup(reply_markup=kb_page)
    await cb.answer()

@router.callback_query(F.data.startswith("admin_media_"))
@admin_only
async def send_media(cb: CallbackQuery, **_):
    idx = int(cb.data.split("_")[2]) - 1
    lst = media_cache.get(cb.from_user.id, [])

    if idx < 0 or idx >= len(lst):
        return await cb.answer("Файл не найден 😕", show_alert=True)

    ftype, fid, cap = lst[idx]

    if ftype == "photo":
        await cb.message.answer_photo(fid, caption=cap)
    elif ftype == "video":
        await cb.message.answer_video(fid, caption=cap)
    elif ftype == "document":
        await cb.message.answer_document(fid, caption=cap)
    elif ftype == "voice":
        # <-- вот эта ветка
        await cb.message.answer_voice(fid, caption=cap)
    else:
        # на всякий случай
        await cb.message.answer_document(fid, caption=cap)

    await cb.answer()



@router.message(F.text == "🔍 Поиск-Профили")
@admin_only
async def ask_search(msg: types.Message, state: FSMContext, **kwargs):
    await state.set_state(SearchUsers.wait_name)
    await msg.answer(
        "Введите имя или его часть для поиска:\n"
        "❌ /search_cancel — отмена",
        reply_markup=kb.admin_menu
    )

@router.message(F.text == "/search_cancel", SearchUsers.wait_name)
@admin_only
async def cancel_search(msg: types.Message, state: FSMContext, **kwargs):
    await state.clear()
    await msg.answer("Поиск отменён.", reply_markup=kb.admin_menu)


# Шаг 2: обрабатываем ввод и выводим результат
@router.message(SearchUsers.wait_name)
@admin_only
async def do_search(msg: types.Message, state: FSMContext, **kwargs):
    query = msg.text.strip()
    # сохраняем запрос
    await state.update_data(last_query=query)
    # переводим состояние в «viewing»
    await state.set_state(SearchUsers.viewing)
    rows = await search_profiles_by_name(query)
    if not rows:
        await state.clear()
        return await msg.answer("🔎 По вашему запросу ничего не найдено.", reply_markup=kb.admin_menu)

    # строим кнопки-результаты
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{r['name']} (ID {r['telegram_id']})",
                callback_data=f"view_profile_{r['telegram_id']}"
            )
        ]
        for r in rows
    ]
    keyboard.append([
        InlineKeyboardButton(text="⏪ Назад к результатам", callback_data="back_to_search_results")
    ])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await msg.answer("🔎 Результаты поиска:", reply_markup=markup)


@router.callback_query(F.data.startswith("view_profile_"))
@admin_only
async def view_profile(cb: types.CallbackQuery, state: FSMContext, **kwargs):
    # парсим ID
    uid = int(cb.data.split("_")[2])
    prof = await get_profile(uid)
    if not prof:
        return await cb.answer("Профиль не найден.", show_alert=True)

    # текст профиля
    text = (
        f"🆔 ID: {uid}\n"
        f"👤 Имя: {prof['name']}\n"
        f"🧬 Пол: {prof['gender']}\n"
        f"📅 Возраст: {prof['age']}\n"
        f"🌆 Город: {prof['location']}\n"
        f"📞 Телефон: {prof['phone']}"
    )
    photo_buf = BufferedInputFile(prof["photo_data"], filename="avatar.jpg")

    # кнопки «Написать» + «Блок/Разблокировать» (reply_kb)
    reply_block_kb = kb.reply_kb_def(uid)

    # кнопка «Бан/Разбан» (admin_profile_kb)
    banned = await is_banned(uid)
    ban_kb    = kb.admin_profile_kb(uid, banned)

    # кнопка «Назад» к списку поиска
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏪ Назад к результатам", callback_data="back_to_search_results")
    ]])

    # объединяем все три клавиатуры
    full_kb = kb.merge_inline(reply_block_kb, ban_kb)
    full_kb = kb.merge_inline(full_kb, back_kb)

    # шлём новое сообщение с полной карточкой
    await cb.message.answer_photo(
        photo=photo_buf,
        caption=text,
        reply_markup=full_kb
    )
    await cb.answer()


@router.callback_query(F.data == "back_to_search_results")
@admin_only
async def back_to_search_results(cb: types.CallbackQuery, state: FSMContext, **kwargs):
    data  = await state.get_data()
    query = data.get("last_query")
    if not query:
        await cb.answer("Запрос не найден.", show_alert=True)
        return

    rows = await search_profiles_by_name(query)
    if not rows:
        await state.clear()
        # удаляем текущее профиль-сообщение
        await cb.message.delete()
        return await cb.message.answer(
            "🔎 По вашему запросу ничего не найдено.",
            reply_markup=kb.admin_menu
        )

    # Удаляем сообщение с подробным профилем
    await cb.message.delete()

    # Строим список кнопок результатов
    keyboard = [
        [InlineKeyboardButton(
            text=f"{r['name']} (ID {r['telegram_id']})",
            callback_data=f"view_profile_{r['telegram_id']}"
        )]
        for r in rows
    ]
    keyboard.append([
        InlineKeyboardButton(text="⏪ Назад к результатам", callback_data="back_to_search_results")
    ])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    # Отправляем новый текстовый список
    await cb.message.answer("🔎 Результаты поиска:", reply_markup=markup)
    await cb.answer()




