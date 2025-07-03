import html
from aiogram.filters import Command
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message ,CallbackQuery , InlineKeyboardButton , InlineKeyboardMarkup , BufferedInputFile

from aiogram.exceptions import TelegramBadRequest
from utils.i18n import t
from database import get_messages_between , get_display_name , get_user_pairs , get_profile , get_user_lang

import hendlers.keybords as kb
from collections import defaultdict
media_cache: dict[int, list[tuple[str, str, str | None]]] = defaultdict(list)



router = Router()


async def safe_edit_text(message, text, **kwargs):
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        if len(e.args) == 0 or "message is not modified" in e.args[0]:
            return
        await message.answer(text, **kwargs)



@router.message(Command("my_chats"))
async def show_user_pairs(msg: types.Message , state: FSMContext):
    user_id = msg.from_user.id
    lang = await get_user_lang(user_id)

    pairs = await get_user_pairs(user_id)

    if not pairs:
        await msg.answer(t("no_chats", locale=lang))
        return

    pairs_with_names = []
    for p_u1, p_u2 in pairs:
        p_name1 = await get_display_name(p_u1) or str(p_u1)
        p_name2 = await get_display_name(p_u2) or str(p_u2)
        pairs_with_names.append((p_u1, p_name1, p_u2, p_name2))

    keyboard = await kb.user_dialog_pairs_kb(
        pairs_with_names,
        current_user_id=user_id,
        media_buttons=None,
        media_offset=0,
        dialogs_offset=0,
    )

    await msg.answer(t("your_dialogs", lang), reply_markup=keyboard)


@router.callback_query(F.data.regexp(r"^user_pair_(\d+)_(\d+)_uid_(\d+)$"))
async def show_user_pair_dialog(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    row = await get_profile(cb.from_user.id)
    lang = row.get("lang") or "ru"

    # Парсим данные из callback_data
    import re
    match = re.match(r"^user_pair_(\d+)_(\d+)_uid_(\d+)$", cb.data)
    if not match:
        return await cb.answer(t("wrong_data_format", lang), show_alert=True)

    u1, u2, uid = map(int, match.groups())
    user_id = cb.from_user.id

    if user_id != uid:
        await cb.answer(t("not_your_session", lang), show_alert=True)
    if user_id not in (u1, u2):
        return await cb.answer(t("no_access_to_dialog", lang), show_alert=True)

    rows = await get_messages_between(u1, u2, 50)

    media_cache[user_id].clear()
    lines = []
    buttons_row = []

    for r in reversed(rows):
        mark = "🟢" if r["sender_id"] == u1 else "⚪"
        ts = r["sent_at"].strftime("%Y-%m-%d %H:%M")
        name = await get_display_name(r["sender_id"]) or str(r["sender_id"])
        safe_body = html.escape(r.get("body", ""), quote=False)
        ft, fid = r.get("file_type"), r.get("file_id")

        icons = {
            "photo": "🖼️",
            "video": "🎥",
            "voice": "📣",
        }

        # если ft есть и есть иконка — берем, иначе дефолт
        logo = icons.get(ft, "📎")

        if ft and fid:
            idx = len(media_cache[user_id]) + 1
            media_cache[user_id].append((ft, fid, safe_body or None))
            icon = "📎"
            buttons_row.append(
                InlineKeyboardButton(
                    text=f"{icon}{idx}",
                    callback_data=f"user_media_{idx}"
                )
            )
            body = f"{logo}={idx} {safe_body}".strip()
        else:
            body = safe_body
        lines.append(f"{mark} {ts} — {name}: {body}")

    text = "\n".join(lines) or t("no_messages", lang)

    pairs = await get_user_pairs(user_id)
    pairs_with_names = []
    for p_u1, p_u2 in pairs:
        p_name1 = await get_display_name(p_u1) or str(p_u1)
        p_name2 = await get_display_name(p_u2) or str(p_u2)
        pairs_with_names.append((p_u1, p_name1, p_u2, p_name2))

    kb_pairs = await kb.user_dialog_pairs_kb(
        pairs_with_names,
        current_user_id=user_id,
        media_buttons=buttons_row,
        media_offset=0,
        dialogs_offset=0,
    )

    name_u1 = await get_display_name(u1) or str(u1)
    name_u2 = await get_display_name(u2) or str(u2)

    await safe_edit_text(
        cb.message,
        f"{t('dialog_with', lang , name = name_u1)} \n\n{text}",
        parse_mode="HTML",
        reply_markup=kb_pairs
    )
    await cb.answer()




@router.callback_query(F.data.regexp(r"^user_media_nav_(\d+)$"))
async def user_media_nav(cb: CallbackQuery):
    offset = int(cb.data.rsplit("_", 1)[1])
    user_id = cb.from_user.id
    row = await get_profile(cb.from_user.id)
    lang = row.get("lang") or "ru"

    all_media_buttons = [
        InlineKeyboardButton(text=f"📎{i+1}", callback_data=f"user_media_{i+1}")
        for i in range(len(media_cache[user_id]))
    ]

    print("hello")
    pairs = await get_user_pairs(user_id)
    kb_page = kb.user_dialog_pairs_kb(pairs, media_buttons=all_media_buttons, offset=offset , lang = lang)
    await safe_edit_text(
        cb.message,
    )

    await cb.message.edit_reply_markup(reply_markup=kb_page)
    await cb.answer()

@router.callback_query(F.data.regexp(r"^user_media_(\d+)$"))
async def send_user_media(cb: CallbackQuery):
    idx = int(cb.data.split("_")[2]) - 1  # <- ВАЖНО: ТУТ ошибка! cb.data.split("_") для 'user_media_1' это ['user', 'media', '1'] => idx=1-1=0 ОК
    user_id = cb.from_user.id
    lst = media_cache.get(user_id, [])
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
        await cb.message.answer_voice(fid, caption=cap)
    else:
        await cb.message.answer_document(fid, caption=cap)
    await cb.answer()




@router.callback_query(F.data.startswith("media_nav_"))
async def paginate_media(cb: CallbackQuery):
    parts = cb.data.split("_")
    media_offset = int(parts[2])
    dialogs_offset = int(parts[4])
    user_id = cb.from_user.id

    # кнопки медиа
    all_media_buttons = [
        InlineKeyboardButton(text=f"📎{i+1}", callback_data=f"user_media_{i+1}")
        for i in range(len(media_cache.get(user_id, [])))
    ]

    # пары
    pairs = await get_user_pairs(user_id)
    pairs_with_names = []
    for u1, u2 in pairs:
        name1 = await get_display_name(u1) or str(u1)
        name2 = await get_display_name(u2) or str(u2)
        pairs_with_names.append((u1, name1, u2, name2))

    kb_page = await kb.user_dialog_pairs_kb(
        pairs_with_names,
        current_user_id=user_id,
        media_buttons=all_media_buttons,
        media_offset=media_offset,
        dialogs_offset=dialogs_offset
    )

    await cb.message.edit_reply_markup(reply_markup=kb_page)
    await cb.answer()



@router.callback_query(F.data.startswith("dialogs_nav_"))
async def paginate_dialogs(cb: CallbackQuery):
    parts = cb.data.split("_")
    dialogs_offset = int(parts[2])
    media_offset = int(parts[4])
    user_id = cb.from_user.id

    # все кнопки медиа
    all_media_buttons = [
        InlineKeyboardButton(text=f"📎{i+1}", callback_data=f"user_media_{i+1}")
        for i in range(len(media_cache.get(user_id, [])))
    ]

    # все пары
    pairs = await get_user_pairs(user_id)
    pairs_with_names = []
    for u1, u2 in pairs:
        name1 = await get_display_name(u1) or str(u1)
        name2 = await get_display_name(u2) or str(u2)
        pairs_with_names.append((u1, name1, u2, name2))

    kb_page = await kb.user_dialog_pairs_kb(
        pairs_with_names,
        current_user_id=user_id,
        media_buttons=all_media_buttons,
        media_offset=media_offset,
        dialogs_offset=dialogs_offset
    )

    await cb.message.edit_reply_markup(reply_markup=kb_page)
    await cb.answer()