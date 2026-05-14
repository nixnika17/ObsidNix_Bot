import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from obsidian_backend import ObsidianManager

print("Success")

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

@bot.message_handler(commands=['stop', 'cancel', 'disactive'])
def cancel_process(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    bot.reply_to(message, "✅ Process is canceled.")

@bot.message_handler(commands=['new'])
def choose_folder(message):
    print(f"Шукаю папки за шляхом: {PATH}")
    print(f"Чи існує папка? {os.path.exists(PATH)}")
    status = os.path.exists(PATH)

    bot.reply_to(message, f"check.. \nШлях: {PATH}\naviable: {'✅ yes' if status else '❌ no'}")
    
    folders = manager.get_folders()
    print(f"Знайдені папки: {folders}")
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📁  (Root)", callback_data="folder_root"))
    
    for folder in folders:
        markup.row(InlineKeyboardButton(f"📁 {folder}", callback_data=f"folder_{folder}"))
        
    bot.reply_to(message, "Обери теку, в якій хочеш зберегти нотатку:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('folder_'))
def handle_folder_selection(call):
    chat_id = call.message.chat.id
    selected_folder = call.data.replace('folder_', '')
    
    # Визначаємо шлях/назву теки
    folder_name = selected_folder if selected_folder != 'root' else '.'
    user_data[chat_id] = {'folder': folder_name}
    
    # Отримуємо список файлів у вибраній теці
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
    try:
        # Отримуємо ім'я файлу, яке ввів користувач
        file_name = message.text.strip()
        
        # Переконуємось, що це не порожній рядок
        if not file_name:
            bot.reply_to(message, "Назва файлу не може бути порожньою. Спробуй ще раз.")
            return

        # Додаємо розширення .md
        if not file_name.endswith('.md'):
            file_name += '.md'

        # Оскільки ми працюємо з текою DUST, використовуємо її
        folder_name = "DUST"

        # Запитуємо у користувача вміст для нотатки, наприклад, просто текст повідомлення (або створюємо порожню нотатку)
        content = "Нотатка створена через інтерфейс бота."
        manager.make_note(content, file_name, folder_name)
        
        bot.reply_to(message, f"Файл {file_name} успішно створено в теці DUST!")
        
    except Exception as e:
        bot.reply_to(message, f"Помилка: {e}")


bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # 1. Отримуємо фото з Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_photo_path = os.path.join(temp_dir, os.path.basename(file_info.file_path))

        with open(temp_photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # 2. Отримуємо підпис (caption), якщо він є
        caption = message.caption if message.caption else ""
        
        # 3. Визначаємо теку, куди все йде
        file_name = "photo_dust.md"
        folder_name = "DUST"

        # 4. Викликаємо наш надійний метод
        manager.append_image_to_note(temp_photo_path, file_name, folder_name, caption=caption)
        
        bot.reply_to(message, "Фото та підпис успішно збережено в теці DUST!")
        
        # 5. Очищаємо тимчасовий файл
        os.remove(temp_photo_path)
        
    except Exception as e:
        bot.reply_to(message, f"Сталася помилка при завантаженні фото: {e}")

# Окремий обробник для звичайного тексту
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        # Якщо ти просто пишеш текст у бот, ми створюємо текстову нотатку
        text_content = message.text
        file_name = "notes_dust.md"
        folder_name = "DUST"
        
        manager.make_note(text_content, file_name, folder_name)
        bot.reply_to(message, "Текстову нотатку успішно додано до теки DUST!")
    except Exception as e:
        bot.reply_to(message, f"Помилка при збереженні тексту: {e}")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        # Якщо ти просто пишеш текст у бот, ми створюємо текстову нотатку
        text_content = message.text
        file_name = "notes_dust.md"
        folder_name = "DUST"
        
        manager.make_note(text_content, file_name, folder_name)
        bot.reply_to(message, "Текстову нотатку успішно додано до теки DUST!")
    except Exception as e:
        bot.reply_to(message, f"Помилка при збереженні тексту: {e}")



def process_name_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
        cancel_process(message)
        return
        
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.reply_to(message, "❌ Помилка: процес було скинуто. Почни знову командою /new.")
        return
        
    user_data[chat_id]['name'] = message.text
    
    msg = bot.reply_to(message, "📄 Текст твоєї нотатки: ")
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
    print("this is main file.bot work.")
    bot.polling(none_stop=True)
