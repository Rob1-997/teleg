from aiogram.types import BotCommand

MESSAGES = {
    "ru": {
        "welcome_back": "🎉<b>  С возвращением !</b>\n👤  <strong>{name}</strong>   ➤ <b>/profile </b> ",
        "ask_gender": "👣 Шаг 1: Выберите ваш пол 🧬",
        "ask_name": "👣 Шаг 2: Как вас зовут ?",
        "ask_age": "👣 Шаг 3: <b>{name}</b> Сколько вам лет ?",
        "ask_location": "👣 Шаг 4: Из какого вы города ?",
        "ask_photo": "👣 Шаг 5: Отправьте <b>фотографию</b> для профиля 📸",
        "reg_done": "✅ Регистрация завершена!",
        "gender_male": "🙍‍♂️ Мужчина",
        "gender_female": "🙍‍♀️ Женщина",
        "continue": "▶️ Далее",
        "back": "⏪ Назад",
        "err_name_nontext": "❗ <i>Пожалуйста, введите ваше имя <b>текстом</b>, без фото или файлов.</i>",
        "err_name_digit": "❗ <i>введите ваше имя <b>текстом</b> минимум 3 символа, не цифрами</i>",
        "err_name_format": "❗ <i>Имя может состоять только из <i><b>букв, пробелов и дефисов.</b>",
        "err_age_nondigit": "❗ <i>Пожалуйста, введите ваш возраст <b>только цифрами</b> Пример: 23</i>",
        "err_age_range": "❗ <i>Укажите возраст от <b>14 до 80</b> лет, например: 25</i>",
        "location": "👣 Шаг {step}: Из какого вы города? Отправьте текст или локацию.",
        "err_age_nontext": "❗ <i>Пожалуйста, введите ваш возраст только <b>цифрами</b>, а не фото или файлом.</i>",
        "photo": "👣 Шаг {step}: Пришлите ваше фото для профиля.",
        "err_location_numeric": "❗ <i>Название города может состоять только </i><b>из букв, не менее 3 символов,</b>",
        "err_location_format": "❗ <i>Название города может содержать только</i> <b>буквы, пробелы или дефис.</b>",
        "err_location_other": "❗ <i>Пожалуйста, укажите город <b>текстом</b> (например, Москва) или нажмите кнопку</i> <b>📍Отправить мою локацию.<b>",
        "err_photo_not_image": "❗ <b>Отправьте только фото</b><i> — остальные форматы не принимаются.</i>",
        "contact": "👣 Последний шаг: Подтвердите ваш номер телефона 📞",
        "err_contact_not_owner": "❗ <i>Подтвердите ваш номер телефона — </i><b>с помощью кнопки</b> ",
        "err_no_photo": "❗ <i>Не вижу фото. Убедитесь, что вы отправили его раньше.</i>",
        "save_profile_error": "😟 Не удалось сохранить анкету: {error}",
        "confirm_caption": (
            "🧬 Пол: {gender}\n"
            "🧑 Имя: {name}\n"
            "📅 Возраст: {age}\n"
            "🌆 Город: {location}\n"
            "📞 Телефон: +{numbers}"
        ),
        "btn_profile": "👤 Профиль",
        "btn_search": "🔍 Поиск",
        "btn_feedback": "✉️ Обратная связь",
        "btn_block_list": "🚫 Блок-лист",
        "block_list_header": "🚫 Ваш список блокировок:",
        "block_list_empty": "Нет заблокированных.",
        "confirm_unblocked": "✅ Пользователь разблокирован.",
        "menu_title": "Главное меню",
        "btn_back": "⏪ Назад",

    },

    "am": {
        "welcome_back": "🎉<b>  Բարի վերադարձ !</b>\n👤  <strong>{name}</strong>   ➤ <b>/profile </b>",
        "ask_gender": "👣 Քայլ 1: Ընտրեք ձեր սեռը 🧬",
        "ask_name": "👣 Քայլ 2: Ինչ է ձեր անունը ?",
        "ask_age": "👣 Քայլ 3: <b>{name}</b> Քանի տարեկան եք ?",
        "ask_location": "👣 Քայլ 4: Որ քաղաքից եք ?",
        "ask_photo": "👣 Քայլ 5: Ուղարկեք <b>լուսանկար</b> պրոֆիլի համար 📸",
        "reg_done": "✅ Գրանցումն ավարտված է!",
        "gender_male": "🙍‍♂️ Տղա",
        "gender_female": "🙍‍♀️ Աղջիկ",
        "continue": "▶️ Շարունակել",
        "back": "⏪ Վերադառնալ",
        "err_name_nontext": "❗ <i>Խնդրում ենք մուտքագրել ձեր անունը <b>տեքստով</b>, ոչ թե լուսանկար կամ ֆայլ։</i>",
        "err_name_digit": "❗ <i>մուտքագրել ձեր անունը <b>տեքստային</b> ձևով առնվազն 3 նիշ, ոչ թե թվերով</i>։",
        "err_name_format": "❗ <i>Անունը կարող է կազմված լինել միայն</i> <b>տառերից, բացատներից , գծերից</b>։",
        "err_age_nondigit": "❗ <i>Խնդրում ենք մուտքագրել ձեր տարիքը <b>միայն թվերով</b> Օրինակ՝ 23</i>",
        "err_age_range": "❗ <i>Մուտքագրեք տարիքը՝ <b>14–80</b> միջակայքում. Օրինակ՝ 25</i>",
        "location": "👣 Քայլ {step}: Որ քաղաքից եք? Ուղարկեք տեքստ կամ դիրքորոշում:",
        "err_age_nontext": "❗ <i>Խնդրում ենք մուտքագրել ձեր տարիքը <b>թվերով</b>, ոչ թե նկարով կամ ֆայլով։</i>",
        "photo": "👣 Քայլ {step}:\n\nՈւղարկեք ձեր պրոֆիլային նկարը։",
        "err_location_numeric": "❗<i>Քաղաքի անունը կարող է կազմված լինել </i><b>միայն տառերից առնվազն 3 նիշ,</b>",
        "err_location_format": "❗ <i>Քաղաքի անունը կարող է պարունակել միայն </i><b>տառեր, բացատներ կամ գծեր </b>։",
        "err_location_other": "❗ <i>Խնդրում եմ նշեք քաղաքը <b>տեքստով</b> (օր.՝ Երևան) կամ օգտագործեք կոճակը</i><b>📍 Ուղարկել իմ գտնվելու վայրը</b>",
        "err_photo_not_image": "❗ <b>Ուղարկեք միայն լուսանկար</b><i> — այլ ֆորմատներ չեն ընդունվում։</i>",
        "contact": "👣 Վերջին քայլը: Հաստատեք ձեր հեռախոսահամարը 📞",
        "err_contact_not_owner": "❗ <i>Հաստատեք Ձեր հեռախոսահամարը՝</i> <b>սեղմելով կոճակը</b>։",
        "err_no_photo": "❗ <i>Չտեսա նկարը. Ստուգեք, արդյոք ուղարկել եք։</i>",
        "save_profile_error": "😟 Անհաջողվեց պահել պրոֆիլը՝ {error}",
        "confirm_caption": (
            "🧬 Սեռ: {gender}\n"
            "🧑 Անուն: {name}\n"
            "📅 Տարիք: {age}\n"
            "🌆 Քաղաք: {location}\n"
            "📞 Հեռախոս: +{numbers}"
        ),
        "btn_profile": "👤 Պրոֆիլ",
        "btn_search": "🔍 Գտնել",
        "btn_feedback": "✉️ Հետադարձ կապ",
        # Новые для блок-листа
        "btn_block_list": "🚫 Արգելափակվածներ",
        "block_list_header": "🚫 Ձեր արգելափակված օգտատերերը՝",
        "block_list_empty": "Արգելափակվածներ չկան։",
        "confirm_unblocked": "✅ Օգտատերը հեռացվել է արգելափակվածներից։",
        "menu_title": "Հիմնական մենյու",
        "btn_back": "⏪ Վերադառնալ",

    },

    "en": {
        "welcome_back": "🎉<b>  Welcome back </b>\n👤  <strong>{name}</strong>   ➤ <b>/profile </b>",
        "reg_done": "✅ Registration complete!",
        "save_profile_error": "😟 Failed to save profile: {error}",
        "err_no_photo": "❗ <i>I don't see a photo. Make sure you sent it.</i>",
        "err_location_format": "❗ <i>City name may contain only </i><b>letters, spaces, or hyphens</b>",
        "err_location_numeric": "❗ <i>City name may consist only </i><b>of letters, at least 3 characters,</b>",
        "err_location_other": "❗ <i>Please enter your city <b>as text</b> (e.g., Moscow) or press the button</i> <b>📍Send my location</b>",
        "edit_age_prompt": "Enter new age (14–80) 📅\n<i>To cancel editing, press</i> /cancel_edit",
        "edit_city_prompt": "Enter new city 🌆\n<i>To cancel editing, press</i> /cancel_edit",
        "edit_name_prompt": "Enter new name ✏️\n<i>To cancel editing, press</i> /cancel_edit",
        "edit_photo_prompt": "Send your new profile photo 📸\n<i>To cancel editing, press</i> /cancel_edit",
        "gender_female": "🙍‍♀️ Female",
        "gender_male": "🙍‍♂️ Male",
        "confirm_caption": (
            "🧬 Gender: {gender}\n"
            "🧑 Name: {name}\n"
            "📅 Age: {age}\n"
            "🌆 City: {location}\n"
            "📞 Phone: +{numbers}"
        ),
        "ask_gender": "👣 Step 1: Select your gender 🧬",
        "ask_name": "👣 Step 2: What is your name?",
        "ask_age": "👣 Step 3: <b>{name}</b> How old are you?",
        "ask_location": "👣 Step 4: What city are you from ?",
        "ask_photo": "Send your profile <b>photo</b> 📸",
        "back": "⏪ Back",
        "err_name_nontext": "❗<i>Please enter your name <b>as text</b>, no photos or files.</i>",
        "err_name_digit": "❗ <i>enter your name in <b>text</b> form at least 3 characters, not digits</i>",
        "err_name_format": "❗ <i>Name may consist only of</i> <b>letters, spaces or hyphens.</b>",
        "err_age_nondigit": "❗ <i>Please enter your age **digits <b>only</b> E.g. 23</i>",
        "err_age_range": "❗ <i>Enter an age between 14 <b>and 80</b>, e.g.: 25</i>",
        "location": "👣 Step {step}: What city are you from? Send text or location.",
        "err_age_nontext": "❗ Please enter your age **as digits**, not as a photo or file.",
        "photo": "👣 Step {step}:\n\nPlease send your profile photo.",
        "err_contact_not_owner": "❗ <i>Confirm your phone number</i> — <b>via the button</b>",
        "err_photo_not_image": "❗ <b>Send only a photo</b><i> — other formats are not accepted.</i>",
        "contact": "👣 Final step: Confirm your phone number 📞",
        "btn_profile": "👤 Profile",
        "btn_search": "🔍 Search",
        "btn_feedback": "✉️ Feedback",
        "btn_block_list": "🚫 Block-list",
        "block_list_header": "🚫 Your block list:",
        "block_list_empty": "No blocked users.",
        "confirm_unblocked": "✅ User has been unblocked.",
        "menu_title": "Main Menu",
        "btn_back": "⏪ Back",

    },

}

MESSAGES.setdefault("ru", {}).update({
    "err_not_registered": "Сначала заполните анкету через регистрацию.\n/start",
    "profile_caption": (
        "👤 <b>Профиль</b>\n\n"
        "🧬 Пол: {gender}\n"
        "🧑 Имя: {name}\n"
        "📅 Возраст: {age}\n"
        "🌆 Город: {location}\n"
        "📞 Телефон: +{phone}"
    ),
})

MESSAGES.setdefault("am", {}).update({
    "err_not_registered": "Առաջին հերթին անցեք գրանցում/ գրանցվել՝ /start",
    "profile_caption": (
        "👤 <b>Պրոֆիլ</b>\n\n"
        "🧬 Սեռ: {gender}\n"
        "🧑 Անուն: {name}\n"
        "📅 Տարիք: {age}\n"
        "🌆 Քաղաք: {location}\n"
        "📞 Հեռախոս: +{phone}"
    ),
})

# (опционально) для английского
MESSAGES.setdefault("en", {}).update({
    "err_not_registered": "First register using /start",
    "profile_caption": (
        "👤 <b>Profile</b>\n\n"
        "🧬 Gender: {gender}\n"
        "🧑 Name: {name}\n"
        "📅 Age: {age}\n"
        "🌆 City: {location}\n"
        "📞 Phone: +{phone}"
    ),
})

MESSAGES["ru"].update({
    "btn_edit": "✏️ Редактировать",
    "edit_name_prompt": "Введите новое имя ✏️ \n<i>Чтобы отменить редактирование, нажмите</i> /cancel_edit",
    "err_edit_name_invalid": "❗ <i>Имя может состоять только</i><b> текстом </b><i>а не цифрами или файлами</i>",
    "edit_name_success": "✅ Имя обновлено.",
    "edit_age_prompt": "Введите новый возраст (14–80) 📅\n<i>Чтобы отменить редактирование, нажмите </i>/cancel_edit",
    "err_edit_age_nondigit": "❗ <i>Возраст — только</i><b> цифрами </b><i>14–80.</i>",
    "err_edit_age_range": "❗ <i>Age must be</i> <b>digits only</b> <i>(14–80).</i>",
    "edit_age_success": "✅ Возраст обновлён.",
    "edit_city_prompt": "Введите новый город 🌆\n<i>Чтобы отменить редактирование, нажмите </i>/cancel_edit",
    "err_edit_city_numeric": "❗ <i>Имя города может состоять только</i><b> текстом </b><i>а не цифрами или файлами</i>",
    "err_edit_city_format": "❗ Название города может содержать только буквы, пробелы и дефис.",
    "edit_city_success": "✅ Город обновлён.",
    "edit_city_geo_success": "✅ Локация принята.",
    "edit_photo_prompt": "Отправьте новое фотографию для профиля 📸\n<i>Чтобы отменить редактирование, нажмите </i>/cancel_edit",
    "err_edit_photo_invalid": "❗ <b>Отправьте только фото</b><i> — остальные форматы не принимаются.</i>",
    "edit_photo_success": "✅ Фото обновлено.",
})

# Армянский
MESSAGES["am"].update({
    "btn_edit": "✏️ Խմբագրել",
    "edit_name_prompt": "Գրեք նոր անունը ✏️ \n<i>Խմբագրումը չեղարկելու համար սեղմեք</i> /cancel_edit",
    "err_edit_name_invalid": "❗ <i>Անունը կարող է կազմված լինել միայն</i><b> տեքստով </b><i>ոչ թե թվերով կամ ֆայլով</i>։",
    "edit_name_success": "✅ Անունը թարմացված է։",
    "edit_age_prompt": "Գրեք նոր տարիքը (14–80) 📅\n<i>Խմբագրումը չեղարկելու համար սեղմեք</i> /cancel_edit",
    "err_edit_age_nondigit": "❗ <i>Տարիքը պետք է լինի միայն</i><b> թվերով </b><i>(14–80)</i>.",
    "err_edit_age_range": "❗ <i>Տարիքը պետք է լինի միայն</i><b> թվերով </b><i>(14–80)</i>",
    "edit_age_success": "✅ Տարիքը թարմացված է։",
    "edit_city_prompt": "Գրեք նոր քաղաքը 🌆\n<i>Խմբագրումը չեղարկելու համար սեղմեք</i> /cancel_edit",
    "err_edit_city_numeric": "❗ <i>Քաղաքի անունը կարող է կազմված լինել միայն</i><b> տեքստով </b><i>ոչ թե թվերով կամ ֆայլով</i>",
    "err_edit_city_format": "❗ Քաղաքի անունը կարող է կազմվել միայն տառերից, բացատներից կամ дефիսից։",
    "edit_city_success": "✅ Քաղաքը թարմացված է։",
    "edit_city_geo_success": "✅ Տեղադրությունը ընդունված է։",
    "edit_photo_prompt": "Ուղարկեք նոր լուսանկար պրոֆիլի համար 📸\n<i>Խմբագրումը չեղարկելու համար սեղմեք</i> /cancel_edit",
    "err_edit_photo_invalid": "❗ <b>Ուղարկեք միայն լուսանկար</b><i> — այլ ֆորմատներ չեն ընդունվում։</i>",
    "edit_photo_success": "✅ Նկարը թարմացված է։",
})

MESSAGES["en"].update({
    "btn_edit": "✏️ Edit",
    "err_edit_age_nondigit": "❗ <i>Age must be</i> <b>digits only</b> <i>(14–80).</i>",
    "err_edit_age_range": "❗ <i>Age must be</i> <b>digits only</b> <i>(14–80).</i>",
    "edit_age_success": "✅ Age updated.",
    "err_edit_name_invalid": "❗ <i>Name may consist only</i><b> of text </b><i>not digits or files</i>",
    "edit_name_success": "✅ Name updated.",
    "err_edit_city_numeric": "❗ <i>City name may consist only</i><b> of text </b><i>not digits or files</i>",
    "err_edit_city_format": "❗ City name can only contain letters, spaces, or hyphens.",
    "edit_city_success": "✅ City updated.",
    "edit_city_geo_success": "✅ Location accepted.",
    "err_edit_city_other": "❗ Please enter the city **as text** or send your location.",
    "edit_photo_success": "✅ Photo updated.",
    "err_edit_photo_invalid": "❗ <b>Send only a photo</b><i> — other formats are not accepted.</i>",

})

MESSAGES.setdefault("ru", {}).update({
    "btn_edit_name": "✏️ Имя",
    "btn_edit_age": "📅 Возраст",
    "btn_edit_city": "🌆 Город",
    "btn_edit_photo": "🖼 Фото",
})

MESSAGES.setdefault("am", {}).update({
    "btn_edit_name": "✏️ Անուն",
    "btn_edit_age": "📅 Տարիք",
    "btn_edit_city": "🌆 Քաղաք",
    "btn_edit_photo": "🖼 Նկար",
})

MESSAGES.setdefault("en", {}).update({
    "btn_edit_name": "✏️ Name",
    "btn_edit_age": "📅 Age",
    "btn_edit_city": "🌆 City",
    "btn_edit_photo": "🖼 Photo",
})

MESSAGES.setdefault("ru", {}).update({
    "sender_caption": "💌 Сообщение от <strong>{name}</strong>:",
    "profile_card_intro": "👤 Пользователь <strong>{name}</strong> хочет вам что-то написать!",
    "profile_card_name": "🧑 Имя: {name}",
    "profile_card_age": "📅 Возраст: {age}",
    "profile_card_city": "🌆 Город: {location}",
})

MESSAGES.setdefault("am", {}).update({
    "sender_caption": "💌 Հաղորդագրություն <strong>{name}</strong> -ից:",
    "profile_card_intro": "👤 Օգտատեր <strong>{name}</strong> ցանկանում է ձեզ գրել:\n",
    "profile_card_name": "🧑 Անուն: {name}",
    "profile_card_age": "📅 Տարիք: {age}",
    "profile_card_city": "🌆 Քաղաք: {location}",
})

MESSAGES.setdefault("en", {}).update({
    "sender_caption": "💌 Message from <strong>{name}</strong>:",
    "profile_card_intro": "👤 User <strong>{name}</strong> wants to write to you!",
    "profile_card_name": "🧑 Name: {name}",
    "profile_card_age": "📅 Age: {age}",
    "profile_card_city": "🌆 City: {location}",
})

MESSAGES["ru"].update({
    'search_end_err': "Попробуйте снова /search, чтобы найти новые профили.",
    "search_end": "Анкеты закончились 🙃",
    "candidate_header": "Вот соседний кандидат:",
    "label_name": "🧑 Имя: {name}",
    "label_age": "📅 Возраст: {age}",
    "label_location": "🌆 Город: {location}",
})

MESSAGES["am"].update({
    "search_end": "Պրոֆիլները վերջացել են 🙃",
    'search_end_err': "Փորձեք կրկին նոր պրոֆիլներ գտնելու համար։ /search",
    "candidate_header": "Ստորև տվյալ մասնակիցն է՝",
    "label_name": "🧑 Անուն: {name}",
    "label_age": "📅 Տարիք: {age}",
    "label_location": "🌆 Քաղաք: {location}",
})

MESSAGES["en"].update({
    'search_end_err': "Try /search again to find new profiles.",
    "search_end": "No more profiles 🙃",
    "candidate_header": "Here’s the next candidate:",
    "label_name": "🧑 Name: {name}",
    "label_age": "📅 Age: {age}",
    "label_location": "🌆 City: {location}",
})

MESSAGES.setdefault("ru", {}).update({
    "btn_chat": "💬 Сообщение",
    "btn_next": "▶️ Далее",
})
MESSAGES.setdefault("am", {}).update({
    "btn_chat": "💬 Հաղորդագրություն",
    "btn_next": "▶️ Հաջորդ",
})
MESSAGES.setdefault("en", {}).update({
    "btn_chat": "💬 Message",
    "btn_next": "▶️ Next",
})

MESSAGES.setdefault("ru", {}).update({
    "err_profile_not_found": "❗ Профиль не найден.",
})
MESSAGES.setdefault("am", {}).update({
    "err_profile_not_found": "❗ Պրոֆիլը չի գտնվել։",
})
MESSAGES.setdefault("en", {}).update({
    "err_profile_not_found": "❗ Profile not found.",
})

MESSAGES.setdefault("ru", {}).update({
    "already_reacted": "Вы уже выбрали эту реакцию.",
    "react_thanks": "Спасибо! 👍{likes} | 👎{dislikes}",
    "notif_intro": "👤 Пользователь <strong>{name}</strong> лайкнул ваш профиль!\n",
    "notif_field_name": "🧑 Имя: {name}",
    "notif_field_age": "📅 Возраст: {age}",
    "notif_field_location": "🌆 Город: {location}",
    "btn_blocking": "🚫 Заблокировать",
})

MESSAGES.setdefault("am", {}).update({
    "already_reacted": "Դուք արդեն ընտրել եք այս ռեակցիան։",
    "react_thanks": "Շնորհակալություն! 👍{likes} | 👎{dislikes}",
    "notif_intro": "👤 Օգտատեր <strong>{name}</strong> հավանեց ձեր պրոֆիլը!\n",
    "notif_field_name": "🧑 Անուն: {name}",
    "notif_field_age": "📅 Տարիք: {age}",
    "notif_field_location": "🌆 Քաղաք: {location}",
    "btn_blocking": "🚫 Արգելափակել",
})

MESSAGES.setdefault("en", {}).update({
    "already_reacted": "You already chose this reaction.",
    "react_thanks": "Thank you! 👍{likes} | 👎{dislikes}",
    "notif_intro": "👤 User <strong>{name}</strong> liked your profile!\n",
    "notif_field_name": "🧑 Name: {name}",
    "notif_field_age": "📅 Age: {age}",
    "notif_field_location": "🌆 City: {location}",
    "btn_blocking": "🚫 Block",
})

MESSAGES.setdefault("ru", {}).update({
    "chat_closed_by_partner": "🚪 Чат закрыт собеседником.",
    "chat_closed": "🚪 Чат закрыт.",
})
MESSAGES.setdefault("am", {}).update({
    "chat_closed_by_partner": "🚪 Զրույցը փակվել է զրուցակցի կողմից։",
    "chat_closed": "🚪 Զրույցը փակվել է։",
})
MESSAGES.setdefault("en", {}).update({
    "chat_closed_by_partner": "🚪 Chat closed by the other user.",
    "chat_closed": "🚪 Chat closed.",
})

MESSAGES.setdefault("ru", {}).update({
    "notif_blocked_you": "🚫 Пользователь заблокировал вас. Вы больше не можете ему писать.",
    "confirm_blocked": "🚫 Пользователь заблокирован.",
    "err_self_blocking": "🚫 Вы заблокировали этого пользователя. Вы не можете ему писать."

})

MESSAGES.setdefault("am", {}).update({
    "notif_blocked_you": "🚫 Օգտատերը արգելափակել է ձեզ։ Չեք կարող նրան գրել։",
    "confirm_blocked": "🚫 Օգտատերը արգելափակված է։",
    "err_self_blocking": "🚫 Դուք արգելափակել եք այս օգտատիրոջը։ Դուք չեք կարող նրան գրել։"

})

MESSAGES.setdefault("en", {}).update({
    "notif_blocked_you": "🚫 You have been blocked and cannot message them.",
    "confirm_blocked": "🚫 User blocked.",
    "err_self_blocking": "🚫 You have blocked this user. You cannot message them."
})

MESSAGES.setdefault("ru", {}).update({
    "err_self_chat": "Это вы сами 🙂",
    "err_not_active": "Пользователь ещё не активировал бота.",
    "chat_opened": "✉️ Чат открыт ! Пишите сообщения.\n<i>Нажмите </i>⏹ Завершить чат, <i>чтобы выйти</i>",
    "chat_partner_connected": "💬 Собеседник подключился к чату!",
    "btn_stop_chat": "⏹ Завершить чат",
})

MESSAGES.setdefault("am", {}).update({
    "err_self_chat": "Դուք չեք կարող զրուցել ինքներդ ձեզ 🙂",
    "err_not_active": "Օգտատերը դեռ չի ակտիվացրել բոտը։",
    "chat_opened": "✉️ Զրույցը սկսված է։ Ուղարկեք ձեր հաղորդագրությունը\n<i>Սեղմեք</i> ⏹ Փակել զրույցը <i>դուրս գալու համար</i>",
    "chat_partner_connected": "💬 Զրուցակիցը միացրեց զրույցին։",
    "btn_stop_chat": "⏹ Փակել զրույցը",
})

MESSAGES.setdefault("en", {}).update({
    "err_self_chat": "You can’t chat with yourself 🙂",
    "err_not_active": "This user hasn’t activated the bot yet.",
    "chat_opened": "✉️ Chat opened! Send your messages.\n<i>Press</i> ⏹ Stop chat <i>to exit</i>",
    "chat_partner_connected": "💬 Your partner has joined the chat!",
    "btn_stop_chat": "⏹ Stop chat",
})

MESSAGES.setdefault("ru", {}).update({
    "btn_reply": "💬 Ответить",
    "btn_block": "🚫 Заблокировать",
    "btn_unblock": "🔓 Разблокировать",
    "btn_cancel": "✅ Отменено",

})
MESSAGES.setdefault("am", {}).update({
    "btn_reply": "💬 Պատասխանել",
    "btn_block": "🚫 Արգելափակել",
    "btn_unblock": "🔓 Անարգելափակել",
    "btn_cancel": "✅ Չեղարկվեց",

})
MESSAGES.setdefault("en", {}).update({
    "btn_reply": "💬 Reply",
    "btn_block": "🚫 Block",
    "btn_unblock": "🔓 Unblock",
    "btn_cancel": "✅ Cancelled",

})

MESSAGES.setdefault("ru", {}).update({
    "ask_feedback": "🛠 <strong>Обратная связь с администрацией</strong>\n\n"
                    "Если у вас есть вопросы, жалобы или идеи по улучшению сервиса — напишите нам. "
                    "Мы обязательно рассмотрим ваше сообщение и дадим ответ в кратчайшие сроки."
                    "\n\n<i>Для отмены обратной связи используйте команду</i> /answer_cancel <i>– Отмена</i>",
    "feedback_received": "✅ Спасибо! Сообщение передано администратору.",
    "ask_reply": "<b>Введите ответ для обращения #{tid}</b>\n\n<i>Для отмены ответа используйте команду</i> /answer_cancel <i>– Отмена</i>",
    "ticket_answered": "👮‍♂️ Ответ по обращению #{tid}:\n\n{text}",
    "reply_sent": "✅ Отправлено администратору",
})

MESSAGES.setdefault("am", {}).update({
    "ask_feedback": "🛠 <strong>Հետադարձ կապ Ադմինիստրացիայի հետ</strong>\n\n"
                    "Եթե ձեզ մոտ կան հարցեր, բողոքներ կամ առաջարկություններ ծառայությունը բարելավելու համար՝ գրեք մեզ։ "
                    "Մենք անպայման կքննարկենք ձեր հաղորդագրությունը և կպատասխանենք հնարավորինս շուտ։ "
                    "\n\n<i>Հետադարձ կապը չեղարկելու համար օգտագործեք</i> /answer_cancel <i>– հրամանը</i>",
    "feedback_received": "✅ Շնորհակալություն! Հաղորդագրությունն ուղարկվեց ադմինիստրատորին։",
    "reply_sent": "✅ Ուղարկվեց ադմինիստրատորին։",
    "ask_reply": "<b>Գրեք պատասխանը դիմումի համար #{tid}</b>\n\n<i>Պատասխանը չեղարկել համար օգտագործեք</i> /answer_cancel <i>– հրամանը</i>",
    "ticket_answered": "👮‍♂️ Պատասխան դիմումի համար #{tid}:\n\n{text}",

})

MESSAGES.setdefault("en", {}).update({
    "ask_feedback": "🛠 <strong>Feedback to Administration</strong> "
                    "If you have any questions, complaints, or suggestions to improve the service, please write to us. "
                    "We will carefully review your message and respond as soon as possible. "
                    "\n\n<i>To cancel the feedback process, use the command</i> /answer_cancel <i>– Cancel</i>",
    "feedback_received": "✅ Thanks! Your message has been sent to the admin.",
    "reply_sent": "✅ Sent to the admin.",
    "ask_reply": "<b>Enter your reply to ticket #{tid}</b>\n\n<i>To cancel your reply, use the command</i> /answer_cancel <i>– Cancel</i>",
    "ticket_answered": "👮‍♂️ Reply to ticket #{tid}:\n\n{text}",

})

MESSAGES["ru"]["answer_sent_admin"] = "✅ Ответ отправлен."
MESSAGES["am"]["answer_sent_admin"] = "✅ Պատասխանն ուղարկվեց ադմինիստրատորին։"
MESSAGES["en"]["answer_sent_admin"] = "✅ Reply sent."

MESSAGES.setdefault("ru", {}).update({
    "answer_cancelled": "✅ Отменено",
})
MESSAGES.setdefault("am", {}).update({
    "answer_cancelled": "✅ Չեղարկվեց",
})
MESSAGES.setdefault("en", {}).update({
    "answer_cancelled": "✅ Cancelled",
})


MESSAGES.setdefault("ru", {}).update({
    "set_reg_lang": "✅ Язык успешно изменён!",
})
MESSAGES.setdefault("am", {}).update({
    "set_reg_lang": "✅ Լեզուն հաջողությամբ փոխվել է!",
})
MESSAGES.setdefault("en", {}).update({
    "set_reg_lang": "✅ Language successfully changed!",
})

MESSAGES.setdefault("ru", {}).update({
    "button_cancel": "Отмена",
    "edit_cancelled": "❌ Редактирование отменено.",
})
MESSAGES.setdefault("am", {}).update({
    "button_cancel": "Չեղարկել",
    "edit_cancelled": "❌ Խմբագրումը չեղարկվեց։",
})
MESSAGES.setdefault("en", {}).update({
    "button_cancel": "❌ Cancel։",
    "edit_cancelled": "❌ Editing cancelled.",
})

MESSAGES.setdefault("ru", {})[
    "err_banned"] = "⛔ Вы заблокированы администратором и не можете пользоваться этим разделом."
MESSAGES.setdefault("am", {})[
    "err_banned"] = "⛔ Ձեզ արգելափակել է ադմինիստրատորը, և դուք չեք կարող օգտագործել այս բաժինը։"
MESSAGES.setdefault("en", {})["err_banned"] = "⛔ You have been banned by the administrator and cannot use this section."

MESSAGES.setdefault("ru", {}).update({
    "err_photo_too_large": "❗ Файл слишком большой (не более {size_mb} МБ).",
    "err_video_too_large": "❗ Видео слишком большое, максимально {size_mb} МБ."

})
MESSAGES.setdefault("am", {}).update({
    "err_photo_too_large": "❗ Ֆայլը շատ մեծ է (առավելագույնում {size_mb} ՄԲ):",
    "err_video_too_large": "❗ Տեսանյութը չափահաս է, առավելագույնը {size_mb} ՄԲ է։"
})
MESSAGES.setdefault("en", {}).update({
    "err_photo_too_large": "❗ File is too large (max {size_mb} MB).",
    "err_video_too_large": "❗ Video is too large; maximum size is {size_mb} MB."
})

COMMANDS = {
    "ru": [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="profile", description="👤 Мой профиль"),
        BotCommand(command="search", description="🔍 Найти собеседника"),
        BotCommand(command="block_list", description="🚫 блок-лист"),
        BotCommand(command="language", description="🌐 Сменить язык"),
        BotCommand(command="feedback", description="✉️ Обратная связь"),
    ],
    "en": [
        BotCommand(command="start", description="🚀 Start the bot"),
        BotCommand(command="profile", description="👤 Show my profile"),
        BotCommand(command="search", description="🔍 Find a partner"),
        BotCommand(command="block_list", description="🚫 block-list"),
        BotCommand(command="language", description="🌐 Change language"),
        BotCommand(command="feedback", description="✉️ Feedback"),
    ],
    "am": [
        BotCommand(command="start", description="🚀 Սկսել բոտը"),
        BotCommand(command="profile", description="👤 Իմ Պրոֆիլ"),
        BotCommand(command="search", description="🔍 Գտնել զրուցակից"),
        BotCommand(command="block_list", description="🚫 Արգելափակվածներ"),
        BotCommand(command="language", description="🌐 Փոխել լեզուն"),
        BotCommand(command="feedback", description="✉️ Հետադարձ կապ"),
    ],
}



def t(key: str, lang: str, **kwargs) -> str:
    """Простой рендер из MESSAGES."""
    template = MESSAGES.get(lang, MESSAGES["ru"]).get(key, "")
    return template.format(**kwargs)
