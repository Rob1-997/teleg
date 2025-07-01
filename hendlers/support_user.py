from aiogram import Router, F, types
from aiogram.types import CallbackQuery , Message
from aiogram.fsm.state  import State, StatesGroup
from aiogram.fsm.context import FSMContext
import hendlers.keybords as kb
from aiogram.filters import Command

from hendlers.hendler import cmd_start
from hendlers.search import cmd_search
from hendlers.blocks import cmd_block_list
from hendlers.language import cmd_set_language
from hendlers.edit_profile import cmd_profile

from database import (
    get_profile,
    get_or_create_thread,
    save_fb_message,
    get_all_admin_ids,
    get_thread_user
)
from utils.i18n import t

router = Router()


class Feedback(StatesGroup):
    wait_text = State()

class UserReply(StatesGroup):
    wait_text = State()



# ─── обычная кнопка «Обратная связь» ────────────────────────────────
@router.message(Command("feedback"))
async def cmd_feedback(msg: Message, state: FSMContext):
    prof = await get_profile(msg.from_user.id)
    if not prof:
        return await msg.answer(t("err_not_registered", "ru"))
    lang = prof["lang"]
    await state.set_state(Feedback.wait_text)
    await msg.answer(t("ask_feedback", lang) , parse_mode="HTML")


@router.message(Feedback.wait_text, F.text)
async def save_feedback(msg: types.Message, state: FSMContext):
    prof = await get_profile(msg.from_user.id)
    if not prof:
        return await msg.answer(
            t("err_not_registered", "ru"),
            reply_markup=kb.not_registration_kb("ru")
        )
    lang = prof.get("lang") or "ru"

    await state.clear()
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


    tid = await get_or_create_thread(msg.from_user.id)
    await save_fb_message(tid, msg.from_user.id, body=msg.text)

    # уведомляем админов
    for aid in await get_all_admin_ids():
        await msg.bot.send_message(
            aid,
            f"🆕 Новое обращение #{tid} от пользователя "
            f"<a href='tg://user?id={msg.from_user.id}'>{msg.from_user.id}</a>",
            parse_mode="HTML",
            reply_markup=kb.admin_thread_kb(tid)
        )

    # отвечаем пользователю
    await msg.answer(t("feedback_received", lang))


@router.callback_query(F.data.regexp(r"^fb_reply_(\d+)$"))
async def ask_user_reply(cb: CallbackQuery, state: FSMContext):
    prof      = await get_profile(cb.from_user.id)
    lang      = prof.get("lang") or "ru"
    thread_id = int(cb.data.split("_")[2])

    await state.set_state(UserReply.wait_text)
    await state.update_data(tid=thread_id)

    # вместо f"..."
    await cb.message.answer(t("ask_reply", lang, tid=thread_id) , parse_mode="HTML")
    await cb.answer()


@router.message(UserReply.wait_text)
async def send_user_reply(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    tid  = data["tid"]

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
    # получаем, кому отправлять
    user_id = await get_thread_user(tid)
    if not user_id:
        return await msg.answer("😕 Тред не найден или закрыт")

    # сохраняем ответ
    await save_fb_message(tid, msg.from_user.id, body=msg.text or f"<{msg.content_type}>")

    # готовим клавиатуру для кнопки «✉️ Ответить»
    prof_u = await get_profile(user_id)
    ulang  = prof_u.get("lang") or "ru"
    kb_to_user = kb.reply_to_thread_kb(tid, ulang)  # без await

    # пересылаем админам
    for aid in await get_all_admin_ids():
        await msg.bot.send_message(
            aid,
            f"🆕 Новое обращение #{tid} от пользователя "
            f"<a href='tg://user?id={msg.from_user.id}'>{msg.from_user.id}</a>",
            parse_mode="HTML",
            reply_markup=kb.admin_thread_kb(tid)
        )

    # отправляем сам ответ пользователю


    lang = (await get_profile(msg.from_user.id)).get("lang") or "ru"
    await msg.answer(t("answer_sent_admin", lang))
    await state.clear()