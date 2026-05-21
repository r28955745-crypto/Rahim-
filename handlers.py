import telebot
from telebot import types
import states
import keyboards
import db_handler
import analyzer
import datetime

def register_handlers(bot: telebot.TeleBot):

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        states.init_user_state(message.from_user.id)
        bot.send_message(
            message.chat.id,
            f"Привет, {message.from_user.first_name}! 👋\n\n"
            "Я твой Трекер Настроения и Продуктивности.",
            reply_markup=keyboards.get_main_keyboard()
        )

    @bot.message_handler(commands=['help'])
    def send_help(message):
        help_text = (
            "*Справка:*\n"
            "/add — Записать данные за сегодня.\n"
            "/stats — График настроения.\n"
            "/history — Все ваши записи.\n"
            "/settings — Настройка напоминаний.\n"
            "/clear — Удалить все данные."
        )
        bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

    @bot.message_handler(commands=['add'])
    def cmd_add(message):
        start_input_process(message)

    @bot.message_handler(func=lambda message: message.text == "➕ Записать день")
    def btn_add(message):
        start_input_process(message)

    @bot.message_handler(commands=['stats'])
    @bot.message_handler(func=lambda m: m.text == "📊 Статистика")
    def show_stats(message):
        user_id = message.from_user.id
        graph_buf = analyzer.generate_mood_graph(user_id)
        
        if graph_buf is None:
            bot.send_message(message.chat.id, "📊 Нет данных для графика. Добавьте запись через /add.")
            return

        bot.send_photo(
            message.chat.id, 
            photo=graph_buf, 
            caption="📈 Ваш график:\nКрасный: Настроение | Зеленый: Учеба | Оранжевый: Сон"
        )

    @bot.message_handler(commands=['history'])
    @bot.message_handler(func=lambda m: m.text == "📜 История")
    def show_history(message):
        user_id = message.from_user.id
        history = db_handler.get_history(user_id)
        
        if not history:
            bot.send_message(message.chat.id, "📜 История пуста. Начните с /add.")
            return

        response = "*Вся история записей:*\n\n"
        for record in reversed(history):
            date_str = record['date'].strftime("%d.%m.%Y")
            comment_str = f"\n💬 _{record['comment']}_ " if record.get('comment') else ""
            
            response += (
                f"*{date_str}*\n"
                f"Настр: {record['mood']}/5 | Учеба: {record['study']}ч | Сон: {record['sleep']}ч"
                f"{comment_str}\n\n"
            )
            
        try:
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        except:
            bot.send_message(message.chat.id, "История слишком длинная для одного сообщения.")

    @bot.message_handler(commands=['settings'])
    @bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
    def show_settings(message):
        bot.send_message(
            message.chat.id,
            "Выберите время ежедневного напоминания:",
            reply_markup=keyboards.get_settings_keyboard()
        )

    @bot.message_handler(commands=['clear'])
    def cmd_clear(message):
        bot.send_message(
            message.chat.id,
            "⚠️ Вы уверены, что хотите удалить ВСЕ данные? Это нельзя отменить.",
            reply_markup=keyboards.get_confirm_clear_keyboard()
        )

    def start_input_process(message):
        user_id = message.from_user.id
        states.init_user_state(user_id)
        msg = bot.send_message(
            message.chat.id,
            "Оцени свое настроение от 1 до 5:",
            reply_markup=keyboards.get_mood_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        user_id = call.from_user.id
        data = call.data

        # --- Mood ---
        if data.startswith('mood_'):
            mood_val = int(data.split('_')[1])
            states.set_state_data(user_id, 'mood', mood_val)
            bot.answer_callback_query(call.id, f"Настроение: {mood_val}")
            
            new_text = f"Настроение: {mood_val}.\n\nЧасы учебы/работы?"
            msg = bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=new_text,
                reply_markup=keyboards.get_hours_keyboard("study")
            )
            bot.register_next_step_handler(msg, process_study_text)

        # --- Study ---
        elif data.startswith('study_'):
            val = data.split('_')[1]
            if val == 'other':
                msg = bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Введите число часов (например, 2.5):",
                    reply_markup=None
                )
                bot.register_next_step_handler(msg, process_study_text)
            else:
                states.set_state_data(user_id, 'study', float(val))
                bot.answer_callback_query(call.id, f"Учеба: {val} ч.")
                go_to_sleep_step(call.message, user_id)

        # --- Sleep ---
        elif data.startswith('sleep_'):
            val = data.split('_')[1]
            if val == 'other':
                msg = bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Сколько часов спал?",
                    reply_markup=None
                )
                bot.register_next_step_handler(msg, process_sleep_text)
            else:
                states.set_state_data(user_id, 'sleep', float(val))
                bot.answer_callback_query(call.id, f"Сон: {val} ч.")
                go_to_comment_step(call.message, user_id)

        # --- Comment skip ---
        elif data == 'comment_skip':
            states.set_state_data(user_id, 'comment', None)
            bot.answer_callback_query(call.id, "Пропущено")
            finish_collection(call.message, user_id)

        # --- Clear confirm ---
        elif data == 'confirm_clear':
            db_handler.clear_history(user_id)
            states.clear_user_state(user_id)
            bot.answer_callback_query(call.id, "Данные очищены")
            bot.edit_message_text("✅ Все данные успешно удалены.", call.message.chat.id, call.message.message_id)
        
        elif data == 'cancel_clear':
            bot.answer_callback_query(call.id, "Отмена")
            bot.delete_message(call.message.chat.id, call.message.message_id)

        # --- Settings reminders ---
        elif data.startswith('set_reminder_'):
            time_str = data.split('_')[2] + ":00"
            bot.answer_callback_query(call.id, f"Напоминание установлено на {time_str}")
            bot.edit_message_text(f"✅ Напоминание установлено на {time_str}.", call.message.chat.id, call.message.message_id)
        
        elif data == 'disable_reminder':
            bot.answer_callback_query(call.id, "Напоминания выключены")
            bot.edit_message_text("❌ Напоминания выключены.", call.message.chat.id, call.message.message_id)


    def process_study_text(message):
        user_id = message.from_user.id
        
        if message.text == "📊 Статистика" or message.text == "/stats":
            show_stats(message)
            return

        try:
            hours = float(message.text.replace(',', '.'))
            if hours < 0: raise ValueError
            states.set_state_data(user_id, 'study', hours)
            go_to_sleep_step(message, user_id)
        except ValueError:
            retry_msg = bot.send_message(message.chat.id, "⚠️ Введено некорректное число. Попробуйте еще раз (например, 2.5):")
            bot.register_next_step_handler(retry_msg, process_study_text)

    def go_to_sleep_step(message_obj, user_id):
        chat_id = message_obj.chat.id
        msg = bot.send_message(
            chat_id, 
            "Сколько часов ты спал?", 
            reply_markup=keyboards.get_hours_keyboard("sleep")
        )
        bot.register_next_step_handler(msg, process_sleep_text)

    def process_sleep_text(message):
        user_id = message.from_user.id
        
        if message.text == "📊 Статистика" or message.text == "/stats":
            show_stats(message)
            return

        try:
            hours = float(message.text.replace(',', '.'))
            if hours < 0 or hours > 24: raise ValueError
            states.set_state_data(user_id, 'sleep', hours)
            go_to_comment_step(message, user_id)
        except ValueError:
            retry_msg = bot.send_message(message.chat.id, "️ Введите число от 0 до 24:")
            bot.register_next_step_handler(retry_msg, process_sleep_text)

    def go_to_comment_step(message, user_id):
        msg = bot.send_message(
            message.chat.id,
            "Добавить комментарий? (Текст или кнопка)",
            reply_markup=keyboards.get_skip_comment_keyboard()
        )
        bot.register_next_step_handler(msg, process_comment_text)

    def process_comment_text(message):
        user_id = message.from_user.id
        states.set_state_data(user_id, 'comment', message.text)
        finish_collection(message, user_id)

    def finish_collection(message, user_id):
        data = states.get_user_data(user_id)
        if not data:
            bot.send_message(message.chat.id, "Ошибка сессии. Начните заново /add")
            return

        db_handler.save_record(
            user_id=user_id,
            mood=data['mood'],
            study_hours=data['study'],
            sleep_hours=data['sleep'],
            comment=data.get('comment')
        )

        summary = (
            f"✅ Данные за {datetime.date.today()} сохранены!\n\n"
            f"🎭 Настроение: {data['mood']}/5\n"
            f"📚 Учеба: {data['study']} ч.\n"
            f"💤 Сон: {data['sleep']} ч.\n"
            f"💬 Комментарий: {data.get('comment', 'Нет')}"
        )
        
        bot.send_message(message.chat.id, summary, reply_markup=keyboards.get_main_keyboard())
        states.clear_user_state(user_id)