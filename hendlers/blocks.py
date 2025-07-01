from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import get_profile, get_blocked, remove_block
from utils.i18n import t
import hendlers.keybords as kb

router = Router()


@router.message(Command("block_list"))
async def cmd_block_list(msg: Message):
    prof = await get_profile(msg.from_user.id)
    if not prof:
        return await msg.answer(
            t("err_not_registered", "ru"),
            reply_markup=kb.not_registration_kb("ru")
        )
    lang = prof["lang"]
    rows = await get_blocked(msg.from_user.id)
    if not rows:
        return await msg.answer(
            t("block_list_empty", lang),
            reply_markup=await kb.menu_for(msg.from_user.id)
        )
    users = [(r["blocked_id"], r["display_name"] or str(r["blocked_id"]))
             for r in rows]
    await msg.answer(
        t("block_list_header", lang),
        reply_markup=kb.blocked_list_kb(lang, users)
    )

# ————————————————————————
# 3) Обработчик разблокировки по callback_data="unblock_<id>"
# ————————————————————————
@router.callback_query(lambda cb: cb.data.startswith("unblock_"))
async def unblock_user(cb: CallbackQuery):
    user_id = cb.from_user.id
    prof    = await get_profile(user_id)
    lang    = prof.get("lang") or "ru"

    target = int(cb.data.split("_",1)[1])
    await remove_block(user_id, target)

    rows = await get_blocked(user_id)
    if not rows:
        await cb.message.edit_text(t("block_list_empty", lang))
        await cb.message.answer(
            t("menu_title", lang),
            reply_markup=await kb.menu_for(user_id)
        )
    else:
        users = [
            (r["blocked_id"], r["display_name"] or str(r["blocked_id"]))
            for r in rows
        ]
        await cb.message.edit_reply_markup(
            reply_markup=kb.blocked_list_kb(lang, users)
        )

    await cb.answer(t("confirm_unblocked", lang))


@router.callback_query(lambda cb: cb.data.startswith("unblock_"))
async def unblock_user(cb: CallbackQuery):
    user_id = cb.from_user.id
    # 1) Язык пользователя
    prof = await get_profile(user_id)
    lang = prof.get("lang") or "ru"

    # 2) Парсим target и удаляем из БД
    target = int(cb.data.split("_", 1)[1])
    await remove_block(user_id, target)

    # 3) Обновляем или закрываем список
    rows = await get_blocked(user_id)
    if not rows:
        # если список пуст
        await cb.message.edit_text(
            t("block_list_empty", lang)
        )
        # и показываем главное меню
        keyboard = await kb.menu_for(user_id)
        await cb.message.answer(
            t("menu_title", lang),
            reply_markup=keyboard
        )
    else:
        # иначе — перестраиваем кнопки
        users = [
            (r["blocked_id"], r["display_name"] or str(r["blocked_id"]))
            for r in rows
        ]
        await cb.message.edit_reply_markup(
            reply_markup=kb.blocked_list_kb(lang, users)
        )

    # 4) Подтверждение операции
    keyboard = await kb.menu_for(user_id)
    await cb.answer(
        t("confirm_unblocked", lang),
        show_alert=False
    )