from aiogram import Router, F, types, Bot
from aiogram.types import CallbackQuery , Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state   import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from io import BytesIO
from utils.i18n import t
from datetime import datetime, timezone, timedelta

import hendlers.keybords as kb

from database import (
    user_exists, set_dialog, get_partner, clear_dialog,
    get_display_name, get_profile , is_blocked, add_block ,remove_block , is_admin , is_banned , save_msg , get_blocked
)

router = Router()
_last_profile_card: dict[tuple[int,int], datetime] = {}
PROFILE_CARD_INTERVAL = timedelta(minutes=1)
_last_close_notify: dict[tuple[int,int], datetime] = {}
CLOSE_NOTIFY_INTERVAL = timedelta(minutes=1)


# ───── FSM для чата ─────
class Chat(StatesGroup):
    talking = State()

# ───── подпись «от кого» ─────
async def sender_caption(user: types.User, lang: str) -> str:
    # Попробуем взять display_name, иначе telegram-имя
    name = await get_display_name(user.id) or user.full_name or user.username
    # Формируем подпись на нужном языке
    return t("sender_caption", lang, name=name)
# (tg://user?id={user.id})
# ───── отправить карточку профиля ─────

async def send_profile_card(bot: Bot, to_id: int, row):
    sender_id = row["telegram_id"]
    recip     = await get_profile(to_id)
    lang      = recip.get("lang") or "ru"

    caption = "\n".join([
        t("profile_card_intro", lang, name=row["name"]),
        t("profile_card_name",  lang, name=row["name"]),
        t("profile_card_age",   lang, age=row["age"]),
        t("profile_card_city",  lang, location=row["location"]),
    ])

    # вот здесь
    reply_kb = await kb.make_reply_block_kb(to_id, sender_id, lang)

    buffer = BytesIO(row["photo_data"])
    await bot.send_photo(
        chat_id=to_id,
        photo=types.BufferedInputFile(buffer.getvalue(), filename="profile.jpg"),
        caption=caption ,
        reply_markup=reply_kb,
        parse_mode="HTML"
    )

@router.callback_query(F.data.regexp(r"^chat_(\d+)$"))
async def start_chat(cb: CallbackQuery, state: FSMContext):
    user_id    = cb.from_user.id
    partner_id = int(cb.data.split("_", 1)[1])
    lang       = (await get_profile(user_id)).get("lang") or "ru"

    # — если я заблокировал партнёра
    if await is_blocked(user_id, partner_id):
        try:
            await cb.message.edit_reply_markup()
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise
        return await cb.message.answer(
            t("notif_blocked_you", lang),
        )

    # — если меня заблокировал партнёр
    if await is_blocked(partner_id, user_id):
        try:
            await cb.message.edit_reply_markup()
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise
        return await cb.message.answer(
            t("err_self_blocking", lang),
        )

    # создаём/обновляем диалоги
    is_new_for_me      = await set_dialog(user_id, partner_id)
    is_new_for_partner = await set_dialog(partner_id, user_id)

    # если партнёр впервые видит — шлём ему карточку профиля,
    # но не чаще раза в минуту
    if is_new_for_partner:
        now = datetime.now(timezone.utc)
        key = (user_id, partner_id)
        last = _last_profile_card.get(key)
        if not last or now - last > PROFILE_CARD_INTERVAL:
            prof = await get_profile(user_id)
            if prof:
                await send_profile_card(cb.bot, partner_id, prof)
            _last_profile_card[key] = now

    # уведомляем инициатора, что чат открыт
    await cb.message.answer(
        t("chat_opened", lang),
        reply_markup=kb.stop_kb(lang) , parse_mode="HTML"
    )
    await cb.answer()
    await state.set_state(Chat.talking)

# ───── Обработка текста внутри чата ─────


@router.message(Chat.talking, F.text)
async def chat_text(msg: Message):
    user_id = msg.from_user.id
    partner = await get_partner(user_id)
    if not partner:
        return

    # 1) Если я заблокировал партнёра или он заблокировал меня — выходим с уведомлением
    if await is_blocked(user_id, partner) or await is_blocked(partner, user_id):
        lang = (await get_profile(user_id)).get("lang") or "ru"
        return await msg.answer(t("notif_blocked_you", lang))

    # 2) Иначе — отправляем сообщение
    plang   = (await get_profile(partner)).get("lang") or "ru"
    caption = await sender_caption(msg.from_user, plang)
    await msg.bot.send_message(
        partner,
        f"{caption}\n\n{msg.text}",
        parse_mode="HTML",
        reply_markup=kb.reply_kb(plang, user_id)
    )
    await save_msg(user_id, partner, text=msg.text)

# ───── Фото ─────
MAX_PHOTO_SIZE = 20 * 1024 * 1024  # 20 МБ

@router.message(Chat.talking, F.photo)
async def chat_photo(msg: Message):
    user_id = msg.from_user.id
    partner = await get_partner(user_id)
    if not partner:
        return

    # проверки блокировок
    if await is_blocked(user_id, partner) or await is_blocked(partner, user_id):
        lang = (await get_profile(user_id)).get("lang") or "ru"
        return await msg.answer(t("notif_blocked_you", lang))

    # берем самую большую версию фото
    photo = msg.photo[-1]
    # проверяем размер
    if photo.file_size and photo.file_size > MAX_PHOTO_SIZE:
        lang = (await get_profile(user_id)).get("lang") or "ru"
        # уведомляем, что фото слишком большое, оставляем ту же inline-клавиатуру «Ответить/Заблокировать»
        return await msg.answer(
            t("err_photo_too_large", lang, size_mb=20),
            reply_markup=kb.reply_kb(lang, user_id)
        )

    # всё ок — пересылаем
    plang   = (await get_profile(partner)).get("lang") or "ru"
    caption = await sender_caption(msg.from_user, plang)
    await msg.bot.send_photo(
        chat_id=partner,
        photo=photo.file_id,
        caption=f"{caption}\n\n{msg.caption or ''}",
        parse_mode="HTML",
        reply_markup=kb.reply_kb(plang, user_id)
    )

    # сохраняем в БД
    await save_msg(
        sender=user_id,
        receiver=partner,
        text=msg.caption,
        file_id=photo.file_id,
        file_type="photo"
    )
# ───── Видео ─────

MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 МБ


@router.message(Chat.talking, F.video)
async def chat_video(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    partner = await get_partner(user_id)
    if not partner:
        return

    # Проверяем блокировки
    if await is_blocked(user_id, partner) or await is_blocked(partner, user_id):
        lang = (await get_profile(user_id)).get("lang") or "ru"
        return await msg.answer(t("notif_blocked_you", lang))

    # Проверяем размер
    if msg.video.file_size and msg.video.file_size > MAX_VIDEO_SIZE:
        lang = (await get_profile(user_id)).get("lang") or "ru"
        # Просто текст ошибки — без кнопок
        return await msg.answer(
            t("err_video_too_large", lang, size_mb=MAX_VIDEO_SIZE // (1024*1024))
        )

    # Всё ок — пересылаем видео партнёру
    plang   = (await get_profile(partner)).get("lang") or "ru"
    caption = await sender_caption(msg.from_user, plang)
    await msg.bot.send_video(
        chat_id=partner,
        video=msg.video.file_id,
        caption=f"{caption}\n\n{msg.caption or ''}",
        parse_mode="HTML",
        reply_markup=kb.reply_kb(plang, user_id)
    )

    # Сохраняем в БД
    await save_msg(
        sender=user_id,
        receiver=partner,
        text=msg.caption,
        file_id=msg.video.file_id,
        file_type="video"
    )


@router.message(Chat.talking, F.voice)
async def chat_voice(msg: Message):
    user_id = msg.from_user.id
    partner = await get_partner(user_id)
    if not partner or await is_blocked(user_id, partner) or await is_blocked(partner, user_id):
        lang = (await get_profile(user_id)).get("lang") or "ru"
        return await msg.answer(t("notif_blocked_you", lang))

    # от кого и подпись
    plang   = (await get_profile(partner)).get("lang") or "ru"
    caption = await sender_caption(msg.from_user, plang)

    # шлём голосовое партнёру
    await msg.bot.send_voice(
        chat_id=partner,
        voice=msg.voice.file_id,
        caption=f"{caption}\n\n{msg.caption or ''}",
        parse_mode="HTML",
        reply_markup=kb.reply_kb(plang, user_id)
    )

    # сохраняем в БД
    try:
        # именно в таком порядке: sender, receiver, text, file_id, file_type
        await save_msg(
            sender=user_id,
            receiver=partner,
            text=msg.caption,         # если у вас caption нет — будет None
            file_id=msg.voice.file_id,
            file_type="voice"
        )
        # простой лог в консоль
        print(f"[save_msg] voice from {user_id} to {partner} saved")
    except Exception as e:
        # если что-то пошло не так — тоже залогируем
        print(f"[save_msg] error saving voice: {e}")


@router.message(Chat.talking, F.document)
async def chat_mov_document(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    partner = await get_partner(user_id)
    if not partner:
        return

    # блокировки
    if await is_blocked(user_id, partner) or await is_blocked(partner, user_id):
        lang = (await get_profile(user_id)).get("lang") or "ru"
        return await msg.answer(t("notif_blocked_you", lang))

    doc = msg.document
    # пропускаем всё, что не видеодокумент
    if not (doc.mime_type and doc.mime_type.startswith("video/")):
        return

    # проверка размера
    if doc.file_size and doc.file_size > MAX_VIDEO_SIZE:
        lang = (await get_profile(user_id)).get("lang") or "ru"
        return await msg.answer(
            t("err_video_too_large", lang, size_mb=MAX_VIDEO_SIZE // (1024*1024))
        )

    # Всё ок — пересылаем как документ, чтобы клиент мог воспроизвести .mov
    plang   = (await get_profile(partner)).get("lang") or "ru"
    caption = await sender_caption(msg.from_user, plang)
    await msg.bot.send_document(
        chat_id=partner,
        document=doc.file_id,
        caption=f"{caption}\n\n{msg.caption or ''}",
        parse_mode="HTML",
        reply_markup=kb.reply_kb(plang, user_id)
    )

    # сохраняем в БД
    await save_msg(
        sender=user_id,
        receiver=partner,
        text=msg.caption,
        file_id=doc.file_id,
        file_type="video"
    )

@router.callback_query(F.data == "chat_stop")
async def stop_chat(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang    = (await get_profile(user_id)).get("lang") or "ru"

    # получаем партнёра и чистим диалоги
    partner_id = await get_partner(user_id)
    await clear_dialog(user_id)
    if partner_id:
        await clear_dialog(partner_id)

        # rate-limit для уведомлений о закрытии
        now = datetime.now(timezone.utc)
        key = (user_id, partner_id)
        last = _last_close_notify.get(key)

        if not last or (now - last) > CLOSE_NOTIFY_INTERVAL:
            # 1) уведомляем партнёра о закрытии
            prow  = await get_profile(partner_id)
            plang = prow.get("lang") or "ru"
            await cb.bot.send_message(
                partner_id,
                t("chat_closed_by_partner", plang),
            )
            _last_close_notify[key] = now

    # сбрасываем состояние и клаву
    await state.clear()
    try:
        await cb.message.edit_reply_markup()
    except TelegramBadRequest:
        pass

    # ответ инициатору
    await cb.message.answer(
        t("chat_closed", lang),
    )
    await cb.answer()

@router.callback_query(F.data.startswith("block_"))
async def block_user(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang    = (await get_profile(user_id)).get("lang") or "ru"
    target  = int(cb.data.split("_",1)[1])

    # 1) Блокируем
    if not await add_block(user_id, target):
        return await cb.answer(t("err_already_blocked", lang), show_alert=True)

    # 2) Очищаем диалог у обоих
    await clear_dialog(user_id)
    await clear_dialog(target)

    # 3) Уведомляем заблокированного, если он активен
    if await user_exists(target):
        tlang = (await get_profile(target)).get("lang") or "ru"
        # 3.1) Сначала — уведомление о том, что его заблокировали
        await cb.bot.send_message(
            target,
            t("notif_blocked_you", tlang),
        )
        # 3.2) Затем — сообщение о закрытии чата
        await cb.bot.send_message(
            target,
            t("chat_closed_by_partner", tlang),
        )

    # 4) Убираем inline-клавиатуру у инициатора
    try:
        await cb.message.edit_reply_markup()
    except TelegramBadRequest as e:
        if "message is not modified" not in e.args[0]:
            raise

    # 5) Сбрасываем состояние FSM у инициатора
    await state.clear()

    # 6) Уведомляем инициатора, что чат закрыт и подтверждаем блокировку
    #    (можно объединить в одно сообщение)
    await cb.message.answer(
        f"{t('chat_closed', lang)}\n{t('confirm_blocked', lang)}",
    )

    await cb.answer()




@router.callback_query(F.data.regexp(r"^unblock_(\d+)$"))
async def unblock_user(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang    = (await get_profile(user_id)).get("lang") or "ru"
    target  = int(cb.data.split("_", 1)[1])

    # 1) Убираем из чёрного списка
    await remove_block(user_id, target)

    # 2) Получаем оставшийся список блокировок
    rows = await get_blocked(user_id)

    if not rows:
        # Если пусто — меняем текст и даём главное меню
        try:
            await cb.message.edit_text(t("block_list_empty", lang))
        except TelegramBadRequest as e:
            if "message is not modified" not in e.args[0]:
                raise

        await cb.message.answer(
            t("menu_title", lang),

        )
    else:
        # Обновляем клавиатуру списка
        users = [(r["blocked_id"], r["display_name"] or str(r["blocked_id"])) for r in rows]
        try:
            await cb.message.edit_reply_markup(
                reply_markup=kb.blocked_list_kb(lang, users)   # синхронная
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in e.args[0]:
                raise

    # 3) Подтверждаем разблокировку
    await cb.answer(t("confirm_unblocked", lang), show_alert=True)