from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.state  import State, StatesGroup
from aiogram.fsm.context import FSMContext
import hendlers.keybords as kb
from utils.i18n import t
from database import (is_admin, list_open_threads, thread_messages,
                      save_fb_message, get_thread_user , get_profile)   # pool понадобится, чтобы узнать user_id

router = Router()

# ─── декоратор ───────────────────────────────────────────────
def admin_only(handler):
    async def wrapper(event, *a, **kw):
        if await is_admin(event.from_user.id):
            return await handler(event, *a, **kw)
        await event.answer("⛔ Только для админа.")
    return wrapper


# ─── СТАДИИ FSM ──────────────────────────────────────────────
class Answer(StatesGroup):
    wait_text = State()       # ждём текст ответа


# ─── список обращений ────────────────────────────────────────
@router.message(F.text == "📬 Обращения")
@admin_only
async def show_threads(msg: types.Message, **_):
    rows = await list_open_threads()
    if not rows:
        return await msg.answer("Нет активных обращений.")
    await msg.answer("Открытые заявки:",
                     reply_markup=kb.admin_threads_list_kb(rows))


# ─── открыть тред ────────────────────────────────────────────
@router.callback_query(F.data.regexp(r"^th_(\d+)$"))
@admin_only
async def open_thread(cb: CallbackQuery, **_):
    tid = int(cb.data.split("_", 1)[1])
    msgs = await thread_messages(tid)
    prof = await get_profile(cb.from_user.id)
    lang = prof.get("lang") or "ru"
    lines = []
    for m in reversed(msgs):
        mark = "👤" if m["sender_id"] != cb.from_user.id else "👮"
        ts   = m["sent_at"].strftime("%d.%m %H:%M")
        body = m["body"] or f"[{m['file_type']}]"
        lines.append(f"{mark} {ts}: {body}")

    await cb.message.edit_text(
        f"Диалог #{tid}\n\n" + ("\n".join(lines) or "пусто"),
        reply_markup=kb.thread_chat_kb(tid, lang)
    )
    await cb.answer()


# ─── нажали «Ответить» ───────────────────────────────────────
@router.callback_query(F.data.regexp(r"^ans_(\d+)$"))
@admin_only
async def ask_answer(cb: CallbackQuery, state: FSMContext, **_):
    tid = int(cb.data.split("_", 1)[1])
    await state.set_state(Answer.wait_text)
    await state.update_data(tid=tid)
    await cb.message.answer(
        f"Введите ответ для обращения #{tid}.\n"
        "Чтобы отменить — /cancel или кнопка ниже.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True, one_time_keyboard=True)
    )
    await cb.answer("Жду текст…")


# ─── отмена ──────────────────────────────────────────────────
@router.message(F.text.in_({"❌ Отмена", "/cancel"}), Answer.wait_text)
async def cancel_answer(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("✅ Отменено.", reply_markup=kb.admin_menu)


# ─── сам ответ ───────────────────────────────────────────────
@router.message(Answer.wait_text, F.text)        # ← уже без «&»
async def send_answer(msg: types.Message, state: FSMContext):
    data    = await state.get_data()
    tid     = data["tid"]
    text    = msg.text

    user_id = await get_thread_user(tid)

    uprofile = await get_profile(user_id)
    ulang = uprofile.get("lang") or "ru"
    # БЕЗ прямого pool.fetchval
    if not user_id:
        await msg.answer("😕 Тред не найден или закрыт")
        return

    await save_fb_message(tid, msg.from_user.id, body=text)

    # отправляем пользователю
    await msg.bot.send_message(
        user_id,
        t("ticket_answered", ulang, tid=tid, text=text),
        reply_markup=kb.reply_to_thread_kb(tid, ulang)
    )
    lang = (await get_profile(msg.from_user.id)).get("lang") or "ru"
    await msg.answer(t("answer_sent_admin", lang ) , reply_markup=kb.admin_menu )
    await state.clear()



