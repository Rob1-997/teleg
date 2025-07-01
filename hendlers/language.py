# hendlers/language.py

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, BotCommandScopeChat
from database import add_user, set_user_language, get_profile, is_admin
from hendlers.keybords import language_kb
from utils.i18n import COMMANDS, t
router = Router()

class Lang(StatesGroup):
    language = State()


@router.message(Command("language"))
async def cmd_set_language(message: Message, state: FSMContext):
    # Убедимся, что у нас есть запись в users
    await add_user(message.from_user.id,
                   message.from_user.username,
                   message.from_user.full_name)
    # Устанавливаем состояние выбора языка и показываем InlineKeyboard
    await state.set_state(Lang.language)
    await message.answer(
        "👋 Select Language / Выберите язык / Ընտրեք լեզուն",
        reply_markup=language_kb , parse_mode="HTML"
    )


@router.callback_query(
    StateFilter(Lang.language),
    F.data.startswith("lang_")
)
async def process_language_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_", 1)[1]

    # 1) Сохраняем язык
    await set_user_language(user_id, lang)

    # 2) Меняем команды бота
    await callback.bot.set_my_commands(
        commands=COMMANDS[lang],
        scope=BotCommandScopeChat(chat_id=user_id)
    )

    await state.clear()

    await callback.message.edit_text(
        t("set_reg_lang", lang)
    )


