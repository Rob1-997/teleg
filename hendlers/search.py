from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile ,Message , InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from datetime import datetime, timezone, timedelta
from database import get_profile, get_profile_by_id, is_admin, is_banned, set_reaction, count_reactions, \
    get_reaction, get_reaction_record , get_candidates_list
from io import BytesIO
import hendlers.keybords as kb

import re
from utils.i18n import t

router = Router()


class Search(StatesGroup):
    candidates = State()
    index      = State()


@router.message(Command(commands=["search"]))
async def cmd_search(msg: Message, state: FSMContext):
    prof = await get_profile(msg.from_user.id)
    if not prof:
        return await msg.answer(
            t("err_not_registered", "ru"),
            reply_markup=kb.not_registration_kb("ru")
        )
    lang = prof["lang"]
    candidates = await get_candidates_list(prof["gender"], msg.from_user.id)
    if not candidates:
        return await msg.answer(
            t("search_end_err", lang),
        )

    await state.set_state(Search.index)
    await state.update_data(candidates=candidates, index=0)
    await _show_current(msg, state, edit=False)


@router.callback_query(F.data == "search_next")
async def next_profile(cb: types.CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    prof    = await get_profile(user_id)
    lang    = prof["lang"] or "ru"

    data       = await state.get_data()
    candidates = data.get("candidates", [])
    if not candidates:
        # вдруг список пуст — выходим в меню
        return await cb.message.answer(
            t("search_end_err", lang),
        )

    # 1) вычисляем новый индекс по кругу
    idx = (data.get("index", 0) + 1) % len(candidates)
    await state.update_data(index=idx)

    # 2) убираем «часики»
    await cb.answer()

    # 3) рисуем карточку с edit=True
    await _show_current(cb.message, state, edit=True)


async def _show_current(
    message: types.Message,
    state:    FSMContext,
    *,
    edit:     bool
):
    data = await state.get_data()
    candidates = data["candidates"]
    idx        = data["index"]
    viewer_id  = message.chat.id

    cand = await get_profile_by_id(candidates[idx])
    lang = (await get_profile(viewer_id))["lang"]

    caption = "\n".join([
        t("label_name",     lang, name=cand["name"]),
        t("label_age",      lang, age=cand["age"]),
        t("label_location", lang, location=cand["location"]),
    ])
    buf   = BytesIO(cand["photo_data"])
    # используем FSInputFile, он точно подойдёт для edit_media
    photo = types.BufferedInputFile(buf.getvalue(), filename="candidate.jpg")

    # строим клавиатуру
    nav_kb = kb.search_nav_kb(lang, cand["telegram_id"])
    if await is_admin(viewer_id):
        banned = await is_banned(cand["telegram_id"])
        nav_kb = kb.merge_inline(nav_kb, kb.admin_profile_kb(cand["telegram_id"], banned))
    react_kb = kb.like_dislike_kb(cand["telegram_id"], await get_reaction(viewer_id, cand["telegram_id"]))
    full_kb = kb.merge_inline(react_kb, nav_kb)

    if edit:
        media = InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML")
        # Попытка 1: edit_media
        try:
            await message.edit_media(media=media, reply_markup=full_kb)
            return
        except TelegramBadRequest as e:
            text = str(e).lower()
            if "not modified" not in text:
                # если это не «не изменено», дальше пробуем
                pass
            else:
                return

        # Попытка 2: edit_caption
        try:
            await message.edit_caption(caption=caption, reply_markup=full_kb, parse_mode="HTML")
            return
        except TelegramBadRequest:
            pass

        # Финальный fallback: удаляем старое и отправляем новое
        try:
            await message.delete()
        except:
            pass
        await message.answer_photo(photo=photo, caption=caption, reply_markup=full_kb)
        return

    # первый показ — новое сообщение
    await message.answer_photo(photo=photo, caption=caption, reply_markup=full_kb)



RETRY_INTERVAL = timedelta(seconds=5)


@router.callback_query(F.data.regexp(r"^reaction_(like|dislike)_(\d+)$"))
async def reaction_handler(cb: types.CallbackQuery):
    user_id = cb.from_user.id
    # язык того, кто ставит реакцию
    me_row = await get_profile(user_id)
    lang   = me_row.get("lang") or "ru"

    # парсим callback_data
    m = re.match(r"reaction_(like|dislike)_(\d+)", cb.data)
    reaction  = m.group(1)           # 'like' или 'dislike'
    target_id = int(m.group(2))

    # 1) посмотрим, что было раньше
    old_rec = await get_reaction_record(user_id, target_id)
    old      = old_rec["reaction"] if old_rec else None
    old_ts   = old_rec["reacted_at"] if old_rec else None

    # 2) если та же реакция — выходим с алертом
    if old == reaction:
        return await cb.answer(
            t("already_reacted", lang),
            show_alert=True
        )

    now = datetime.now(timezone.utc)
    send_notification = False

    # 3) определяем, надо ли уведомлять
    if reaction == "like":
        if old is None:
            send_notification = True
        elif old != reaction and old_ts and (now - old_ts) > RETRY_INTERVAL:
            send_notification = True

    # 4) сохраняем новую реакцию
    await set_reaction(user_id, target_id, reaction)

    # 5) обновляем клавиатуру под карточкой
    likes, dislikes = await count_reactions(target_id)
    # навигация поиска локализована внутри search_nav_kb
    nav_kb = kb.search_nav_kb(lang, target_id)
    if await is_admin(user_id):
        banned   = await is_banned(target_id)
        admin_kb = kb.admin_profile_kb(target_id, banned)
        nav_kb   = kb.merge_inline(nav_kb, admin_kb)
    react_kb = kb.like_dislike_kb(target_id, reaction)
    full_kb  = kb.merge_inline(react_kb, nav_kb)

    try:
        await cb.message.edit_reply_markup(reply_markup=full_kb)
    except TelegramBadRequest:
        pass

    # 6) благодарим пользователя
    await cb.answer(
        t("react_thanks", lang, likes=likes, dislikes=dislikes)
    )

    # 7) отправляем уведомление тому, чей профиль лайкнули
    if not send_notification:
        return

    liker = await get_profile(user_id)
    if not liker:
        return

    # язык получателя уведомления
    target_row = await get_profile(target_id)
    lang_to    = target_row.get("lang") or "ru"

    # формируем подпись-уведомление
    buf = BytesIO(liker["photo_data"])
    photo = types.BufferedInputFile(buf.getvalue(), filename="user.jpg")

    caption = "\n".join([
        t("notif_intro",            lang_to, name=liker["name"]),
        t("notif_field_name",       lang_to, name=liker["name"]),
        t("notif_field_age",        lang_to, age=liker["age"]),
        t("notif_field_location",   lang_to, location=liker["location"]),
    ])

    # кнопка «Написать»
    buttons = [
        InlineKeyboardButton(
            text=t("btn_chat", lang_to),
            callback_data=f"chat_{user_id}"
        )
    ]
    # и (для админа-получателя) кнопка «Заблокировать»
    if await is_admin(target_id):
        buttons.append(
            InlineKeyboardButton(
                text=t("btn_block", lang_to),
                callback_data=f"block_{user_id}"
            )
        )

    # реакции в обратную сторону
    back = await get_reaction(target_id, user_id)
    back_kb = kb.like_dislike_kb(user_id, back)

    notif_kb = InlineKeyboardMarkup(inline_keyboard=[buttons])
    notif_kb = kb.merge_inline(back_kb, notif_kb)

    await cb.bot.send_photo(
        chat_id=target_id,
        photo=photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=notif_kb
    )
