import telebot
import config
import handlers

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="Markdown")
handlers.register_handlers(bot)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)