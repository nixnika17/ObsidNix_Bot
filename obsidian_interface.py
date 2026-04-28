import telebot

from obsidian_backend import ObsidianManager


print("Бібліотека підключена успішно!")

TOKEN = "8013227418:AAG1Zsx8ydA1Zavkjw-pw3TJyunJbWvIRMM"
PATH = "/mnt/g/My Drive/NIX WORKSHOπ"

manager = ObsidianManager(PATH)
bot = telebot.TeleBot(TOKEN)


# bot = telebot.TeleBot(TOKEN, manager = ObsidianManager(PATH)) # You can set parse_mode by default. HTML or MARKDOWN,parse_mode=None

# @bot.message_handler(commands=['start', 'help'])

@bot.message_handler(func=lambda message: True)
def hundler(message):
       try:
                path = manager.make_note(content=message.text, file_name = "")
                bot.reply_to(message, "🟩🟩🟩") #✅✅✅🟥🟥🟥🟩🟩🟩
       except Exception as e:
                bot.reply_to(message, f"🟥 Помилка: {e}")

print("Бот запущений...")
bot.polling(none_stop=True)
