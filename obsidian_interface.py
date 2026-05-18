import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from obsidian_backend import ObsidianManager


# АНАЛІЗ КОДУ ТА ПРОЦЮВАТИ НАД ФУНКЦІЯМИ ФОТО


TOKEN = "8013227418:AAG1Zsx8ydA1Zavkjw-pw3TJyunJbWvIRMM"
PATH =  "/mnt/g/My Drive/NIX WORKSHOP"

manager = ObsidianManager(PATH)
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hey,Nix!I'm your obsidian-manager.\n\n")

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Created by Nix Vail.\n\nThis program will help you make your notes faster and easier.")

@bot.message_handler(commands=['author'])
def send_author(message):
    bot.reply_to(message, "created by Nix Vail.\n\nContact: vasilishenanika@gmail.com\ntg: @nikavaslnix\nsocial media:\ngithub: https://github.com/nixnika17\n\ntgk: https://t.me/nixinworld")

@bot.message_handler(commands=['stop', 'cancel'])
def cancel_process(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    bot.reply_to(message, "Контекст скинуто. Напиши назву нової теки або обери зі списку.")
    
    # bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    # bot.reply_to(message, "✅ Process is canceled.")

@bot.message_handler(commands=['new'])
def choose_folder(message):
    print(f"Шукаю папки за шляхом: {PATH}")
    print(f"Чи існує папка? {os.path.exists(PATH)}")
    status = os.path.exists(PATH)

    bot.reply_to(message, f"check.. \npath: {PATH}\naviable: {'✅ yes' if status else '❌ no'}")
    
    folders = manager.get_folders()
    print(f"Знайдені папки: {folders}")
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📁  (Root)", callback_data="folder_root"))
    
    for folder in folders:
        markup.row(InlineKeyboardButton(f"📁 {folder}", callback_data=f"folder_{folder}"))

        
    bot.reply_to(message, "choose exist or make new folder:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('folder_'))
def handle_folder_selection(call):
    chat_id = call.message.chat.id
    selected_folder = call.data.replace('folder_', '')
    

    folder_name = selected_folder if selected_folder != 'root' else '.'
    user_data[chat_id] = {'folder': folder_name}
    
    files = manager.get_files(folder_name if folder_name != "." else "")
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("➕ Створити новий файл", callback_data="create_new_file"))
    
    for file in files:
        file_display = file.replace('.md', '')
        markup.row(InlineKeyboardButton(f"📄 {file_display}", callback_data=f"file_{file}"))
        
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.id,
        text=f"📂 Вибрано теку: {folder_name}.\n\n file for add or make new:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('file_') or call.data == 'create_new_file')
def handle_file_selection(call):
    chat_id = call.message.chat.id
    
    if call.data == 'create_new_file':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.id,
            text="📝 Напиши назву нового файлу (без .md):"
        )
        bot.register_next_step_handler(call.message, process_name_step)
    else:
        selected_file = call.data.replace('file_', '')
        user_data[chat_id]['name'] = selected_file
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.id,
            text=f"📄 Вибрано файл: {selected_file}.\n\nНапиши текст, який хочеш додати до файлу:"
        )
        bot.register_next_step_handler(call.message, process_append_content_step)


def process_name_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
        cancel_process(message)
        return
        
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.reply_to(message, "❌ Помилка: процес було скинуто. Почни знову /new.")
        return
        

    user_data[chat_id]['name'] = message.text
    

    msg = bot.reply_to(message, "📄 Тепер напиши текст твоєї нотатки:")
    bot.register_next_step_handler(msg, process_content_step)


@bot.message_handler(content_types=['photo'])
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        chat_id = message.chat.id
        
        # Перевіряємо, чи є дані в пам'яті, і чи вони не None
        current_data = user_data.get(chat_id, {})
        
        # Використовуємо .get() з дефолтними значеннями, щоб уникнути None
        target_file = current_data.get('name') 
        if target_file is None:
            target_file = "Unsorted_Photos" # Назва за замовчуванням
            
        target_folder = current_data.get('folder')
        if target_folder is None:
            target_folder = "DUST" # Папка за замовчуванням

        # ... (тут твій код завантаження фото) ...

        # Виклик бекенду (тепер ми впевнені, що тут рядки, а не None)
        manager.append_image_to_note(
            photo_path=temp_photo_path, 
            file_name=str(target_file), # Примусово перетворюємо на рядок
            folder_name=str(target_folder), 
            caption=caption if caption else ""
        )
        
        bot.reply_to(message, f"✅ Збережено у файл: {target_file}")
        
    except Exception as e:
        print(f"Full error: {e}") # Це допоможе тобі побачити деталі в консолі
        bot.reply_to(message, f"🟥 Error: {e}")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data or 'folder' not in user_data[chat_id]:
        
        existing_folders = manager.get_folders()
        
        if text in existing_folders:
            user_data[chat_id] = {'folder': text}
            bot.reply_to(message, f"✅ Folder '{text}' chosen. now send text or photo for notes.")
        else:
            try:
                full_path = os.path.join(PATH, text)
                os.makedirs(full_path, exist_ok=True)
                
                user_data[chat_id] = {'folder': text}
                bot.reply_to(message, f"📂 Створено нову теку '{text}' та обрано її. Тепер можеш писати нотатки сюди!")
            except Exception as e:
                bot.reply_to(message, f"❌ Помилка при створенні теки: {e}")
        
        return 

    try:
        folder_name = user_data[chat_id]['folder']
        
        # Передаємо: 
        # 1. Текст (content)
        # 2. "." (file_name) -> це змусить бекенд спрацювати за логікою if not file_name...
        # 3. Назву папки (folder_name)
        manager.make_note(text, ".", folder_name)
        
        bot.reply_to(message, f"📝 Нотатку збережено в '{folder_name}'!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Помилка: {e}")
 


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
        bot.send_message(chat_id, f"✅ Нотатку збережено: {file_res}\nу теку: {folder}")
        
        del user_data[chat_id]
    except Exception as e:
        bot.send_message(message.chat.id, f"🟥 Error: {e}")


def process_append_content_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
        cancel_process(message)
        return
        
    try:
        chat_id = message.chat.id
        folder = user_data[chat_id]['folder']
        file_name = user_data[chat_id]['name']
        new_content = message.text
        
        full_path = manager.append_to_note(
            content=new_content,
            file_name=file_name,
            folder_name=folder if folder != "." else ""
        )
        
        file_res = os.path.basename(full_path)
        bot.send_message(chat_id, f"✅ Успішно додано до файлу: {file_res}\nу теку: {folder}")
        
        del user_data[chat_id]
    except Exception as e:
        bot.send_message(message.chat.id, f"🟥 Error: {e}")

if __name__ == '__main__':
    print("this is main file.  bot work.")
    bot.polling(none_stop=True)
