from telebot import types

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn_add = types.KeyboardButton("➕ Записать день")
    btn_stats = types.KeyboardButton("📊 Статистика")
    btn_history = types.KeyboardButton("📜 История")
    btn_settings = types.KeyboardButton("⚙️ Настройки")
    
    markup.row(btn_add, btn_stats)
    markup.row(btn_history, btn_settings)
    
    return markup

def get_mood_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [
        types.InlineKeyboardButton("1 😫", callback_data="mood_1"),
        types.InlineKeyboardButton("2 😐", callback_data="mood_2"),
        types.InlineKeyboardButton("3 🙂", callback_data="mood_3"),
        types.InlineKeyboardButton("4 😊", callback_data="mood_4"),
        types.InlineKeyboardButton("5 🤩", callback_data="mood_5"),
    ]
    markup.add(*buttons)
    return markup

def get_hours_keyboard(prefix):
    markup = types.InlineKeyboardMarkup(row_width=4)
    if prefix == "study":
        options = ["0.5", "1", "2", "3", "4", "5"]
    else:
        options = ["6", "7", "8", "9", "10"]
    
    buttons = [types.InlineKeyboardButton(f"{opt} ч", callback_data=f"{prefix}_{opt}") for opt in options]
    btn_other = types.InlineKeyboardButton("Свое...", callback_data=f"{prefix}_other")
    
    markup.add(*buttons)
    markup.add(btn_other)
    return markup

def get_skip_comment_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Пропустить", callback_data="comment_skip"))
    return markup

def get_confirm_clear_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Да, удалить всё", callback_data="confirm_clear"))
    markup.add(types.InlineKeyboardButton("Нет", callback_data="cancel_clear"))
    return markup

def get_settings_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(" Напоминать в 21:00", callback_data="set_reminder_21"))
    markup.add(types.InlineKeyboardButton(" Напоминать в 23:00", callback_data="set_reminder_23"))
    markup.add(types.InlineKeyboardButton(" Выключить напоминания", callback_data="disable_reminder"))
    return markup