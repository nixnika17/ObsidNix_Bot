<<<<<<< HEAD
import telebot
import os

from obsidian_backend import ObsidianManager


print("Success")

TOKEN = "8013227418:AAG1Zsx8ydA1Zavkjw-pw3TJyunJbWvIRMM"
PATH = "/mnt/g/My Drive/NIX WORKSHOπ"

manager = ObsidianManager(PATH)
bot = telebot.TeleBot(TOKEN)

user_data = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hey,Nix!   I'm your obsidian-manager.\n\n")

@bot.message_handler(commands=['info'])
def send_welcome(message):
    bot.reply_to(message, "Created by Nix Vail.\n\nThis program will help you make your notes faster and easier.")

@bot.message_handler(commands=['author'])
def send_welcome(message):
    bot.reply_to(message, "created by Nix Vail.\n\nContact: vasilishenanika@gmail.com" "\n|" "tg: @nikavaslnix" "\nsocial media:" "\ngithub: https://github.com/nixnika17" "\n\ntgk: https://t.me/nixinworld")

# canceling
@bot.message_handler(commands=['stop', 'cancel', 'disactive'])
def cancel_process(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id] # delete data
    
    # чистка для наступних кроків
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    bot.reply_to(message, "process is cancel")

@bot.message_handler(commands=['new'])
def folder(message):
    msg = bot.reply_to(message, "📂 name of folder | . for root")
    bot.register_next_step_handler(msg, process_folder_step)

def process_folder_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
            cancel_process(message)
            return
    chat_id = message.chat.id
    user_data[chat_id] = {'folder': message.text}
    msg = bot.reply_to(message, "📝 name of file (without .md):")
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
            cancel_process(message)
            return #exit
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    msg = bot.reply_to(message, "📄 your note: ")
    bot.register_next_step_handler(msg, process_content_step)

def process_content_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
            cancel_process(message) 
            return
    try:
        chat_id = message.chat.id
        folder = user_data[chat_id]['folder']
        name = user_data[chat_id]['name']
        content = message.text

        full_path = manager.make_note(
            content=content, 
            file_name=name, 
            folder_name=folder if folder != "." else ""
        )
        
        file_res = os.path.basename(full_path)
        bot.send_message(chat_id, f"✅ Save note {file_res}\n in folder: {folder} ")
        
        # Очищуємо пам'ять
        del user_data[chat_id]
    except Exception as e:
        bot.send_message(message.chat.id, f"🟥 Eroor: {e}")


print("Bot work...")
bot.polling(none_stop=True)
=======
import telebot
import os

from obsidian_backend import ObsidianManager


print("Success")

TOKEN = "8013227418:AAG1Zsx8ydA1Zavkjw-pw3TJyunJbWvIRMM"
PATH = "/mnt/g/My Drive/NIX WORKSHOπ"

manager = ObsidianManager(PATH)
bot = telebot.TeleBot(TOKEN)

user_data = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hey,Nix!<: I'm your obsidian-manager.\n\n Let's make notes!! ")

@bot.message_handler(commands=['info'])
def send_welcome(message):
    bot.reply_to(message, "Created by *Nix Vail*.\n\n~This program will help you make your notes faster and easier.")

@bot.message_handler(commands=['author'])
def send_welcome(message):
    bot.reply_to(message, "Hey,Nix!<: I'm your obsidian-manager.\n\n Let's make notes!! ")

# canceling
@bot.message_handler(commands=['stop', 'cancel', 'disactive'])
def cancel_process(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id] # delete data
    
    # чистка для наступних кроків
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    bot.reply_to(message, "process is cancel")

@bot.message_handler(commands=['new'])
def folder(message):
    msg = bot.reply_to(message, "📂 name of folder | . for root")
    bot.register_next_step_handler(msg, process_folder_step)

def process_folder_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
            cancel_process(message)
            return
    chat_id = message.chat.id
    user_data[chat_id] = {'folder': message.text}
    msg = bot.reply_to(message, "📝 name of file (without .md):")
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
            cancel_process(message)
            return #exit
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    msg = bot.reply_to(message, "📄 your note: ")
    bot.register_next_step_handler(msg, process_content_step)

def process_content_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
            cancel_process(message) 
            return
    try:
        chat_id = message.chat.id
        folder = user_data[chat_id]['folder']
        name = user_data[chat_id]['name']
        content = message.text

        full_path = manager.make_note(
            content=content, 
            file_name=name, 
            folder_name=folder if folder != "." else ""
        )
        
        file_res = os.path.basename(full_path)
        bot.send_message(chat_id, f"✅ Save note {file_res}\n in folder: {folder} 🟩")
        
        # Очищуємо пам'ять
        del user_data[chat_id]
    except Exception as e:
        bot.send_message(message.chat.id, f"🟥 Eroor: {e}")


print("Bot work...")
bot.polling(none_stop=True)
>>>>>>> 94aa6737e9a75b1ba2336f88455e9e0901a32f14
