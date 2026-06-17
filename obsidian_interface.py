import os
import shutil
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from obsidian_backend import ObsidianManager

print("--- ТЕРМІНАЛ ПЕРЕЗАВАНТАЖЕНО ---")

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

    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.id,
            text=f"📂 Вибрано теку: {folder_name}.\n\n file for add or make new:",
            reply_markup=markup
        )
    except telebot.apihelper.ApiTelegramException as e:
        if "not modified" in str(e):
            bot.answer_callback_query(call.id, "✅ Тека вже обрана")
        else:
            raise


@bot.callback_query_handler(func=lambda call: call.data.startswith('file_') or call.data == 'create_new_file')
def handle_file_selection(call):
    chat_id = call.message.chat.id

    if chat_id not in user_data:
        bot.answer_callback_query(call.id, "❌ Спочатку вибери теку")
        return

    try:
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
    except telebot.apihelper.ApiTelegramException as e:
        if "not modified" in str(e):
            bot.answer_callback_query(call.id, "✅ Вже обрано")
        else:
            raise


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

# ЗАЙМИСЬ ТУТ
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print("!!! ПРИЙНЯТО ФОТО В ІНТЕРФЕЙСІ !!!")
    try:
        chat_id = message.chat.id
        
        # 1. Отримуємо фото від Telegram
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # 2. Зберігаємо тимчасово
        temp_path = f"temp_{file_id}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(downloaded_file)
        
        # 3. БЕЗПЕЧНО витягуємо дані (використовуємо .get, щоб не було KeyError)
        user_info = user_data.get(chat_id, {})
        
        # Якщо user_info['name'] порожній або None, беремо "Unsorted"
        target_file = user_info.get('name') or "Unsorted_Photos"
        target_folder = user_info.get('folder') or "DUST"
        
        caption = message.caption or ""

        print(f"DEBUG: Передаю в бекенд: {target_file} у папку {target_folder}")

        # 4. Виклик бекенду
        # Переконайся, що в obsidian_backend.py метод називається саме так!
        manager.append_image_to_note(
            photo_path=temp_path, 
            file_name=target_file, 
            folder_name=target_folder, 
            caption=caption
        )
        
        bot.reply_to(message, f"📸 Фото додано в: {target_file}")

    except Exception as e:
        import traceback
        print("❌ КРИТИЧНА ПОМИЛКА В ІНТЕРФЕЙСІ:")
        traceback.print_exc() # ЦЕ НАЙВАЖЛИВІШИЙ РЯДОК ЗАРАЗ
        bot.reply_to(message, f"❌ Помилка: {e}")

# ДАЛІ ВСЕ СПРАВНО


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
