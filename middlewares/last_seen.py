from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext
from database import is_banned, is_admin , get_profile
from hendlers.support_user import Feedback, UserReply
from utils.i18n import t

class UpdateLastSeen(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # event может быть Message, CallbackQuery и т.д.
        if hasattr(event, "from_user"):
            from database import update_last_seen   # локальный импорт во избежание циклов
            await update_last_seen(event.from_user.id)
        return await handler(event, data)

class CheckBan(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Только для апдейтов от пользователя
        if hasattr(event, "from_user"):
            uid = event.from_user.id

            # Если залочен и не админ
            if await is_banned(uid) and not await is_admin(uid):
                # вытащим язык
                prof = await get_profile(uid)
                lang = prof.get("lang") or "ru"

                # 1) Разрешаем кнопку «Обратная связь»
                if isinstance(event, types.Message) and event.text == t("btn_feedback", lang):
                    return await handler(event, data)

                # 2) Разрешаем ввод в состоянии обратной связи
                state: FSMContext | None = data.get("state")
                if state:
                    current = await state.get_state()
                    if current in (Feedback.wait_text.state, UserReply.wait_text.state):
                        return await handler(event, data)

                # 3) Разрешаем любые CallbackQuery, связанные с обратной связью
                if isinstance(event, types.CallbackQuery) and event.data and event.data.startswith("fb_"):
                    return await handler(event, data)

                # Во всех остальных случаях — показываем алерт
                ban_msg = t("err_banned", lang)  # добавьте в MESSAGES ключ "err_banned"
                if isinstance(event, types.CallbackQuery):
                    await event.answer(ban_msg, show_alert=True)
                else:
                    await event.answer(ban_msg)
                # прерываем дальнейшую обработку
                return

        # Если не забанен или админ — дальше по цепочке
        return await handler(event, data)