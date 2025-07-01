from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# … другие нужные вам классы …

async def copy_with_profile(
    bot: Bot,
    to_user_id: int,
    from_user_profile: dict,
    forwarded_msg: types.Message
):
    """
    Пересылаем профилированное сообщение админа (или пользователя),
    сохраняя «имя в боте» и разные мелочи.
    """
    # Пример: сначала — отправляем карточку профиля (фото + подпись)
    photo_path = from_user_profile["photo_path"]
    caption = (
        f"🧑 Имя: {from_user_profile['name']}\n"
        f"📅 Возраст: {from_user_profile['age']}\n"
        f"🌆 Город: {from_user_profile['location']}\n"
        f"📱 Телеграм: @{from_user_profile.get('username', '')}"
    )

    await bot.send_photo(
        chat_id=to_user_id,
        photo=types.FSInputFile(photo_path),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Ответить", callback_data=f"fb_reply_{forwarded_msg.message_id}")]
            ]
        )
    )

    # А потом непосредственный форвард сообщения
    await forwarded_msg.copy_to(to_user_id)
