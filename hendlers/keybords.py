from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import is_admin , get_profile , is_blocked , is_banned , get_user_lang
from utils.i18n import t


language_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="lang_am"),
    ],
    [
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
    ],
])

def feedback_kb(lang: str) -> ReplyKeyboardMarkup:
    """
    Клавиатура, содержащая только кнопку «Обратная связь» на нужном языке.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [ KeyboardButton(text=t("btn_feedback", lang)) ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def gender_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("gender_male",   lang), callback_data="male"),
            InlineKeyboardButton(text=t("gender_female", lang), callback_data="female"),
        ],
    ])

cont = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Շարունակել', callback_data='continue')],
])

def location_kb(lang: str) -> ReplyKeyboardMarkup:
    text = {
        "ru": "📍 Отправить мою локацию",
        "am": "📍 Ուղարկել իմ գտնվելու վայրը"
    }.get(lang, "📍 Send my location")
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text, request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def contact_kb(lang: str) -> ReplyKeyboardMarkup:
    text = {
        "ru": "📞 Отправить мой номер",
        "am": "📞 Ուղարկել իմ հեռախոսահամարը",
        "en": "📞 Send my number"
    }.get(lang, "📞 Send my number")
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def not_registration_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_feedback", lang))]],
        resize_keyboard=True
    )



def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    keys = ["btn_profile", "btn_search", "btn_block_list", "btn_feedback"]
    # [["Профиль"], ["Поиск"], ...]

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(key, lang))] for key in keys],
        resize_keyboard=True
)


# new
def main_menu_inline(lang: str) -> InlineKeyboardMarkup:
    # Здесь ключи — это те же самые ключи из MESSAGES, которые вы передавали
    buttons = [
        ("btn_profile",    "menu_profile"),
        ("btn_search",     "menu_search"),
        ("btn_block_list", "menu_block_list"),
        ("btn_feedback",   "menu_feedback"),
    ]
    kb = InlineKeyboardMarkup(row_width=1)
    for msg_key, cb_data in buttons:
        kb.insert(
            InlineKeyboardButton(
                text=t(msg_key, lang),
                callback_data=cb_data
            )
        )
    return kb



main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="🔍 Поиск")],
        [KeyboardButton(text="🚫 Блок-лист")],
        [KeyboardButton(text="✉️ Обратная связь")],
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🟢 Онлайн 24 ч"), KeyboardButton(text="⬇️ Экспорт CSV")],
        [KeyboardButton(text="🔍 Поиск")    , KeyboardButton(text="📨 Рассылка")],
        [KeyboardButton(text="🚫 Блок-лист"), KeyboardButton(text="🚫 Бан-лист")],  # ← НОВАЯ
        [KeyboardButton(text="👀 Переписки") , KeyboardButton(text="📬 Обращения")],
        [KeyboardButton(text="🔍 Поиск-Профили") ,KeyboardButton(text="🔙 Выйти из админки")],
    ],
    resize_keyboard=True
)

async def menu_for(user_id: int) -> ReplyKeyboardMarkup:
    """
    • Если user_id — админ → возвращаем admin_menu
    • Иначе → читаем его lang из профиля и возвращаем main_menu_kb(lang)
    """
    if await is_admin(user_id):
        return admin_menu

    prof = await get_profile(user_id)
    lang = prof.get("lang") if prof and prof.get("lang") else "ru"



def edit_entry_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [ InlineKeyboardButton(text=t("btn_edit", lang),
                              callback_data="edit_menu") ]
    ])




def profile_actions_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_edit_name",  lang), callback_data="edit_name") , InlineKeyboardButton(text=t("btn_edit_age",   lang), callback_data="edit_age")],
        [InlineKeyboardButton(text=t("btn_edit_city",  lang), callback_data="edit_city") , InlineKeyboardButton(text=t("btn_edit_photo", lang), callback_data="edit_photo")],
    ])


def search_nav_kb(lang: str, target_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для поиска: только кнопки «Написать» и «Далее».
    """
    btn_chat = InlineKeyboardButton(
        text=t("btn_chat", lang),
        callback_data=f"chat_{target_id}"
    )
    btn_next = InlineKeyboardButton(
        text=t("btn_next", lang),
        callback_data="search_next"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_chat],
            [btn_next]
        ]
    )

# ───── кнопка «Ответить» ─────
def reply_kb(lang: str, sender_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("btn_reply", lang),
            callback_data=f"chat_{sender_id}"
        ),
        InlineKeyboardButton(
            text=t("btn_block", lang),
            callback_data=f"block_{sender_id}"
        )
    ]])

def reply_kb_def(sender_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="💬 Ответить",
                callback_data=f"chat_{sender_id}"
            ),
            InlineKeyboardButton(
                text="🚫 Заблокировать",
                callback_data=f"block_{sender_id}"
            )
        ]]
    )


async def make_reply_block_kb(recipient_id: int, sender_id: int, lang: str) -> InlineKeyboardMarkup:
    """
    Формирует клавиатуру: [💬 Ответить]  [🚫 Заблокировать / 🔓 Разблокировать]
    на языке получателя.
    """
    # выбираем правильный текст кнопки блокировки
    if await is_blocked(recipient_id, sender_id):
        block_btn = InlineKeyboardButton(
            text=t("btn_unblock", lang),
            callback_data=f"unblock_{sender_id}"
        )
    else:
        block_btn = InlineKeyboardButton(
            text=t("btn_block", lang),
            callback_data=f"block_{sender_id}"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("btn_reply", lang), callback_data=f"chat_{sender_id}"),
        block_btn
    ]])

    # если получатель — админ, добавляем ещё кнопки бан/разбан
    if await is_admin(recipient_id):
        banned = await is_banned(sender_id)
        admin_kb = admin_profile_kb(sender_id, banned)
        # сливаем две клавиатуры
        kb.inline_keyboard += admin_kb.inline_keyboard

    return kb

async def reply_block_kb(recipient_id: int, sender_id: int, lang: str) -> InlineKeyboardMarkup:
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from database import is_blocked, is_admin, is_banned

    btn_reply = InlineKeyboardButton(
        text=t("btn_reply", lang),
        callback_data=f"chat_{sender_id}"
    )
    if await is_blocked(recipient_id, sender_id):
        btn_block = InlineKeyboardButton(
            text=t("btn_unblock", lang),
            callback_data=f"unblock_{sender_id}"
        )
    else:
        btn_block = InlineKeyboardButton(
            text=t("btn_block", lang),
            callback_data=f"block_{sender_id}"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[[btn_reply, btn_block]])

    # При необходимости добавляем админ-кнопки дальше…
    if await is_admin(recipient_id):
        banned   = await is_banned(sender_id)
        kb.inline_keyboard += admin_profile_kb(sender_id, banned).inline_keyboard

    return kb




# ───── кнопка «Завершить чат» ─────
def stop_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("btn_stop_chat", lang),
            callback_data="chat_stop"
        )
    ]])

def block_kb(target_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚫 Заблокировать",
                callback_data=f"block_{target_id}"
            )]
        ]
    )

def blocked_list_kb(lang: str, users: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"🔓 {name}", callback_data=f"unblock_{uid}")]
        for uid, name in users
    ]
    rows.append([
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_profile_kb(uid: int, is_banned: bool) -> InlineKeyboardMarkup:
    btn = (
        InlineKeyboardButton(text="🔓 Разбан", callback_data=f"admin_unban_{uid}")
        if is_banned else
        InlineKeyboardButton(text="⛔ Бан",     callback_data=f"admin_ban_{uid}")
    )
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])

# ── список банов ──

def bans_list_kb(rows: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    # строим список рядов: каждая строка — список кнопок
    keyboard = [
        [InlineKeyboardButton(
            text=f"🔓 {name}",
            callback_data=f"admin_unban_{uid}"
        )]
        for uid, name in rows
    ]
    # кнопка «в меню» внизу
    keyboard.append([
        InlineKeyboardButton(text="⏪ В меню", callback_data="back_menu")
    ])

    # создаём разметку сразу с inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def merge_inline(kb1: InlineKeyboardMarkup, kb2: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """
    Возвращает новую клавиатуру = кнопки kb1 + kb2.
    """
    return InlineKeyboardMarkup(inline_keyboard = kb1.inline_keyboard + kb2.inline_keyboard)

bcast_cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

def bcast_confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ Отправить", callback_data="bcast_send"),
            InlineKeyboardButton(text="❌ Отмена",    callback_data="bcast_cancel")
        ]]
    )





def dialogs_list_kb(users: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """
    users: [(uid, display_name), …]
    На каждой кнопке будет «Имя (uid)».
    """
    keyboard: list[list[InlineKeyboardButton]] = []
    for user  in users:
        uid = user['uid']
        name = user['name']
        keyboard.append([
            InlineKeyboardButton(
                text=f"{uid} ({name})",
                callback_data=f"admin_dialog_{uid}"
            )
        ])

    # кнопка «Назад» внизу
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_dialog_back"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def dialog_back_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_dialog_back")]
        ]
    )


PAGE_SIZE = 8

def dialog_pairs_kb(
    users: list[dict],
    media_buttons: list[InlineKeyboardButton] | None = None,
    offset: int = 0
) -> InlineKeyboardMarkup:
    """
    • users — список пар {'u1':…, 'u2':…}
    • media_buttons — список InlineKeyboardButton(text="📎N", callback_data="admin_media_nav_idx")
    • offset — смещение для пагинации media_buttons
    """
    keyboard: list[list[InlineKeyboardButton]] = []

    # 1) В одну строку вкладываем page = media_buttons[offset:offset+PAGE_SIZE]
    if media_buttons:
        page = media_buttons[offset : offset + PAGE_SIZE]
        if page:
            # весь page — одна строка
            keyboard.append(page)

        # навигация между «страницами» скрепок
        nav: list[InlineKeyboardButton] = []
        if offset > 0:
            nav.append(
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"admin_media_nav_{offset - PAGE_SIZE}"
                )
            )
        if offset + PAGE_SIZE < len(media_buttons):
            nav.append(
                InlineKeyboardButton(
                    text="▶️ Далее",
                    callback_data=f"admin_media_nav_{offset + PAGE_SIZE}"
                )
            )
        if nav:
            keyboard.append(nav)

    # 2) Кнопки «u1 ↔ u2» по одной на строку
    for pair in users:
        u1, u2 = pair['u1'], pair['u2']
        keyboard.append([
            InlineKeyboardButton(
                text=f"{u1} ↔ {u2}",
                callback_data=f"admin_pair_{u1}_{u2}"
            )
        ])

    # 3) Кнопка «Назад» в самом низу
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_admin")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_thread_kb(tid: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть", callback_data=f"th_{tid}")
    ]])

def admin_threads_list_kb(rows) -> InlineKeyboardMarkup:
    """
    rows — список записей из list_open_threads()
    """
    keyboard: list[list[InlineKeyboardButton]] = []

    for r in rows:
        # #12 • 123456789 • Привет…
        preview = (r["last_msg"] or "")[:20] + "…" if r["last_msg"] else "—"
        keyboard.append([
            InlineKeyboardButton(
                text=f"#{r['id']} • {r['user_id']} • {preview}",
                callback_data=f"th_{r['id']}"
            )
        ])

    # ← вот эта строка была с позиционным арг-ом — ставим text=
    keyboard.append([
        InlineKeyboardButton(
            text="⏪ Назад",
            callback_data="back_admin"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def thread_chat_kb(tid: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("btn_reply", lang),
                callback_data=f"ans_{tid}"
            )
        ],
        [
            InlineKeyboardButton(
                text=t("btn_back", lang),
                callback_data="back_admin"
            )
        ],
    ])

def reply_to_thread_kb(thread_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text=t("btn_reply", lang),
                callback_data=f"fb_reply_{thread_id}"
            )
        ]]
    )

# new like dislike

def like_dislike_kb(target_id: int, current: str | None) -> InlineKeyboardMarkup:
    like_text    = f"👍 {'' if current!='like' else '✅'}"
    dislike_text = f"👎 {'' if current!='dislike' else '✅'}"
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=like_text,    callback_data=f"reaction_like_{target_id}"),
        InlineKeyboardButton(text=dislike_text, callback_data=f"reaction_dislike_{target_id}")
    ]])





async def user_dialog_pairs_kb(
    pairs: list[tuple[int, str, int, str]],
    current_user_id: int,
    media_buttons: list[InlineKeyboardButton] | None = None,
    media_offset: int = 0,
    dialogs_offset: int = 0,
    media_page_size: int = 5,
    dialogs_page_size: int = 8,
) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    lang = await get_user_lang(current_user_id)

    # --- Медиа кнопки и пагинация
    if media_buttons:
        media_page = media_buttons[media_offset:media_offset + media_page_size]
        if media_page:
            keyboard.append(media_page)

        media_nav = []
        if media_offset > 0:

            media_nav.append(InlineKeyboardButton(
                text=f"◀️ {t('media_btn_back', lang)}",
                callback_data=f"media_nav_{media_offset - media_page_size}_do_{dialogs_offset}"
            ))
        if media_offset + media_page_size < len(media_buttons):
            media_nav.append(InlineKeyboardButton(
                text=f"{t('media_btn_next', lang)} ▶️",
                callback_data=f"media_nav_{media_offset + media_page_size}_do_{dialogs_offset}"
            ))

        if media_nav:
            keyboard.append(media_nav)

    # --- Диалоги и пагинация
    unique_pairs = {}
    for u1, name1, u2, name2 in pairs:
        key = tuple(sorted((u1, u2)))
        if key not in unique_pairs:
            unique_pairs[key] = (name1, name2) if key[0] == u1 else (name2, name1)

    dialog_keys = list(unique_pairs.items())
    dialog_page = dialog_keys[dialogs_offset:dialogs_offset + dialogs_page_size]

    for (id1, id2), (n1, n2) in dialog_page:
        keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {n1} ",
                callback_data=f"user_pair_{id1}_{id2}_uid_{current_user_id}"
            )
        ])

    dialog_nav = []
    if dialogs_offset > 0:
        dialog_nav.append(InlineKeyboardButton(
            text=f"◀️ {t('dialogs', lang)}",
            callback_data=f"dialogs_nav_{dialogs_offset - dialogs_page_size}_mo_{media_offset}"
        ))
    if dialogs_offset + dialogs_page_size < len(dialog_keys):
        dialog_nav.append(InlineKeyboardButton(
            text=f"▶️ {t('dialogs', lang)}",
            callback_data=f"dialogs_nav_{dialogs_offset + dialogs_page_size}_mo_{media_offset}"
        ))
    if dialog_nav:
        keyboard.append(dialog_nav)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


