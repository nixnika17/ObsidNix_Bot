import os
import shutil
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from obsidian_backend import ObsidianManager
from dotenv import load_dotenv
from telebot import types

print("--- ТЕРМІНАЛ ПЕРЕЗАВАНТАЖЕНО ---")

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


def resolve_vault_path():
    candidates = [
        os.getenv("OBSIDIAN_PATH"),
        os.getenv("VAULT_PATH"),
        r"G:\My Drive\NIX WORKSHOP",
        r"D:\My Drive\NIX WORKSHOP",
        "/mnt/g/My Drive/NIX WORKSHOP",
        os.path.join(os.getcwd(), "NIX WORKSHOP"),
        os.path.join(os.getcwd(), "ObsidianVault"),
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    return candidates[0] or os.getcwd()


PATH = resolve_vault_path()
manager = ObsidianManager(PATH)
bot = telebot.TeleBot(TOKEN)

user_data = {}


def get_note_target(chat_id):
    user_info = user_data.get(chat_id, {})
    target_file = user_info.get('name') or "Unsorted_Photos"
    target_folder = user_info.get('folder') or "DUST"
    return target_file, target_folder


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    btn_new = types.KeyboardButton("/new")
    btn_read = types.KeyboardButton("/read")
    btn_stop = types.KeyboardButton("/stop")

    markup.add(btn_new, btn_read, btn_stop)
    return markup


# ---------------------- ПРОСТІ КОМАНДИ ----------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Hey,Nix!i'm your bot.",
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Created by Nix Vail.\n\nThis program will help you make your notes faster and easier.")


@bot.message_handler(commands=['author'])
def send_author(message):
    bot.reply_to(
        message,
        "created by Nix Vail.\n\nContact: vasilishenanika@gmail.com\ntg: @nikavaslnix\n"
        "social media:\ngithub: https://github.com/nixnika17\n\ntgk: https://t.me/nixinworld"
    )


@bot.message_handler(commands=['stop', 'cancel'])
def cancel_process(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    bot.reply_to(message, "Контекст скинуто. Напиши назву нової теки або обери зі списку.")


@bot.message_handler(commands=['photos', 'photo'])
def command_photos(message):
    chat_id = message.chat.id
    target_file, target_folder = get_note_target(chat_id)
    user_data[chat_id] = {**user_data.get(chat_id, {}), 'photo_mode': True}
    bot.reply_to(
        message,
        f"📸 Готово до прийому фото. Надішліть фото з текстом/підписом.\n"
        f"Збережу у файл: {target_file}\nу теку: {target_folder}"
    )


# ---------------------- ВИБІР ТЕКИ (спільне для /new і /read, з підтримкою вкладених тек) ----------------------

def show_folder_contents(chat_id, path_parts, action, message=None, call=None):
    rel_path = os.path.join(*path_parts) if path_parts else ""

    subfolders = manager.get_folders(rel_path)
    files = manager.get_files(rel_path)

    user_data[chat_id]['action'] = action
    user_data[chat_id]['path_parts'] = path_parts
    user_data[chat_id]['folder_options'] = subfolders
    user_data[chat_id]['folder'] = rel_path if rel_path else "."

    markup = InlineKeyboardMarkup()

    nav_row = []
    if path_parts:
        nav_row.append(InlineKeyboardButton("⬆️ Назад", callback_data="folder_up"))
        nav_row.append(InlineKeyboardButton("🏠 Корінь", callback_data="folder_root"))
    if nav_row:
        markup.row(*nav_row)

    for i, folder in enumerate(subfolders):
        markup.row(InlineKeyboardButton(f"📁 {folder}", callback_data=f"folder_idx_{i}"))

    if action == 'add':
        markup.row(InlineKeyboardButton("➕ Створити новий файл тут", callback_data="create_new_file"))

    for file in files:
        file_display = file.replace('.md', '')
        markup.row(InlineKeyboardButton(f"📄 {file_display}", callback_data=f"file_{file}"))

    current_label = " / ".join(path_parts) if path_parts else "(Root)"
    label = "додати текст/фото" if action == 'add' else "прочитати"
    text = f"📂 Поточна тека: {current_label}\n\nОбери підтеку, або файл щоб {label}:"

    if call:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.id, text=text, reply_markup=markup)
        except telebot.apihelper.ApiTelegramException as e:
            if "not modified" in str(e):
                bot.answer_callback_query(call.id, "✅ Ок")
            else:
                raise
    else:
        bot.reply_to(message, text, reply_markup=markup)


@bot.message_handler(commands=['new'])
def choose_folder(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'action': 'add', 'path_parts': []}
    show_folder_contents(chat_id, [], 'add', message=message)


@bot.message_handler(commands=['read'])
def choose_folder_for_reading(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'action': 'read', 'path_parts': []}
    show_folder_contents(chat_id, [], 'read', message=message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('folder_'))
def handle_folder_selection(call):
    chat_id = call.message.chat.id

    if chat_id not in user_data:
        user_data[chat_id] = {'action': 'add', 'path_parts': []}

    data = call.data[len('folder_'):]
    action = user_data[chat_id].get('action', 'add')
    path_parts = user_data[chat_id].get('path_parts', [])

    if data == 'root':
        path_parts = []
    elif data == 'up':
        path_parts = path_parts[:-1]
    elif data.startswith('idx_'):
        idx = int(data[len('idx_'):])
        options = user_data[chat_id].get('folder_options', [])
        if idx < len(options):
            path_parts = path_parts + [options[idx]]

    show_folder_contents(chat_id, path_parts, action, call=call)


# ---------------------- ВИБІР ФАЙЛУ (розгалуження add / read) ----------------------

@bot.callback_query_handler(func=lambda call: call.data.startswith('file_') or call.data == 'create_new_file')
def handle_file_selection(call):
    chat_id = call.message.chat.id

    if chat_id not in user_data:
        bot.answer_callback_query(call.id, "❌ Спочатку вибери теку")
        return

    action = user_data[chat_id].get('action', 'add')

    try:
        if call.data == 'create_new_file':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.id,
                text="📝 Напиши назву нового файлу (без .md):"
            )
            bot.register_next_step_handler(call.message, process_name_step)
            return

        selected_file = call.data.replace('file_', '')

        if action == 'read':
            folder = user_data[chat_id]['folder']
            content = manager.read_note(selected_file, folder if folder != "." else "")

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.id,
                text=f"📄 {selected_file}"
            )

            if content is None:
                bot.send_message(chat_id, "❌ Файл не знайдено.")
            elif not content.strip():
                bot.send_message(chat_id, "📭 Файл порожній.")
            else:
                for i in range(0, len(content), 4000):
                    bot.send_message(chat_id, content[i:i + 4000])

            del user_data[chat_id]
            return

        # режим 'add' — стара логіка
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


# ---------------------- СТВОРЕННЯ НОВОГО ФАЙЛУ ----------------------

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


def process_content_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
        cancel_process(message)
        return
    try:
        chat_id = message.chat.id
        folder = user_data[chat_id]['folder']
        name = user_data[chat_id]['name']

        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            ext = os.path.splitext(file_info.file_path)[1] or ".jpg"
            temp_path = os.path.join(os.getcwd(), f"temp_{file_id}{ext}")
            with open(temp_path, 'wb') as f:
                f.write(downloaded_file)

            caption = (message.caption or "").strip()

            manager.append_image_to_note(
                photo_path=temp_path,
                file_name=name,
                folder_name=folder if folder != "." else "",
                caption=caption,
            )
            bot.send_message(chat_id, f"📸 Фото додано у файл: {name}")
            del user_data[chat_id]
            return

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
        import traceback
        traceback.print_exc()
        bot.send_message(message.chat.id, f"🟥 Error: {e}")


def process_append_content_step(message):
    if message.text in ['/stop', '/cancel', '/disactive']:
        cancel_process(message)
        return

    try:
        chat_id = message.chat.id
        folder = user_data[chat_id]['folder']
        file_name = user_data[chat_id]['name']

        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            ext = os.path.splitext(file_info.file_path)[1] or ".jpg"
            temp_path = os.path.join(os.getcwd(), f"temp_{file_id}{ext}")
            with open(temp_path, 'wb') as f:
                f.write(downloaded_file)

            caption = (message.caption or "").strip()

            manager.append_image_to_note(
                photo_path=temp_path,
                file_name=file_name,
                folder_name=folder if folder != "." else "",
                caption=caption,
            )
            bot.send_message(chat_id, f"📸 Фото додано у файл: {file_name}")
            del user_data[chat_id]
            return

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
        import traceback
        traceback.print_exc()
        bot.send_message(message.chat.id, f"🟥 Error: {e}")


# ---------------------- ФОТО ПОЗА ФЛОУ /new (через /photo) ----------------------

def process_photo_caption_step(message, photo_path, target_file, target_folder):
    if message.text in ['/stop', '/cancel', '/disactive']:
        cancel_process(message)
        return

    try:
        caption = (message.text or "").strip()
        manager.append_image_to_note(
            photo_path=photo_path,
            file_name=target_file,
            folder_name=target_folder,
            caption=caption,
        )
        bot.reply_to(message, f"📸 Фото з текстом додано в: {target_file}")
    except Exception as e:
        import traceback
        print("❌ ПОМИЛКА ПРИ ОБРОБЦІ ТЕКСТУ ДО ФОТО:")
        traceback.print_exc()
        bot.reply_to(message, f"❌ Помилка: {e}")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print("!!! ПРИЙНЯТО ФОТО В ІНТЕРФЕЙСІ !!!")
    try:
        chat_id = message.chat.id

        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        ext = os.path.splitext(file_info.file_path)[1] or ".jpg"
        temp_path = os.path.join(os.getcwd(), f"temp_{file_id}{ext}")
        with open(temp_path, 'wb') as f:
            f.write(downloaded_file)

        target_file, target_folder = get_note_target(chat_id)
        caption = (message.caption or "").strip()

        print(f"DEBUG: Передаю в бекенд: {target_file} у папку {target_folder}")

        if not caption and user_data.get(chat_id, {}).get('photo_mode'):
            user_data[chat_id]['photo_mode'] = False
            user_data[chat_id]['pending_photo'] = {
                'photo_path': temp_path,
                'target_file': target_file,
                'target_folder': target_folder,
            }
            msg = bot.reply_to(message, "✍️ Напиши текст для фото:")
            bot.register_next_step_handler(
                msg,
                lambda next_message: process_photo_caption_step(
                    next_message,
                    user_data[chat_id]['pending_photo']['photo_path'],
                    user_data[chat_id]['pending_photo']['target_file'],
                    user_data[chat_id]['pending_photo']['target_folder'],
                ),
            )
            return

        user_data.setdefault(chat_id, {})
        user_data[chat_id].pop('photo_mode', None)
        manager.append_image_to_note(
            photo_path=temp_path,
            file_name=target_file,
            folder_name=target_folder,
            caption=caption,
        )

        bot.reply_to(message, f"📸 Фото додано в: {target_file}")

    except Exception as e:
        import traceback
        print("❌ КРИТИЧНА ПОМИЛКА В ІНТЕРФЕЙСІ:")
        traceback.print_exc()
        bot.reply_to(message, f"❌ Помилка: {e}")


# ---------------------- ЗАГАЛЬНИЙ ТЕКСТОВИЙ ХЕНДЛЕР ----------------------

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
        manager.make_note(text, ".", folder_name)
        bot.reply_to(message, f"📝 Нотатку збережено в '{folder_name}'!")
    except Exception as e:
        bot.reply_to(message, f"❌ Помилка: {e}")


if __name__ == '__main__':
    print("this is main file.  bot work.")
    bot.polling(none_stop=True)