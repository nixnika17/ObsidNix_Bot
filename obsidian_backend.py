# PROTOTYPE №1

from datetime import datetime  # time
import os  # operation system
import shutil
import re


class ObsidianManager:
    def __init__(self, parent_path):  # вказування шляху
        if not parent_path:
            raise ValueError("❌ here should be a parent_path!")
        self._parent_path = parent_path

    def _clean_string(self, text):  # чистка заборонених символів
        forbidden = r'\\/:*?"<>|'
        text = str(text or "")
        for char in forbidden:
            text = text.replace(char, "")
        return text.strip()

    def create_folder(self, folder_name):  # склеювання шляху, parent vault
        folder_name = str(folder_name or "").strip()

        # "." або порожньо -> це корінь vault, нову підтеку не створюємо
        if folder_name in (".", ""):
            os.makedirs(self._parent_path, exist_ok=True)
            return self._parent_path

        # Розбиваємо шлях на окремі рівні (працює і з "\", і з "/"),
        # щоб не втратити вкладеність при чистці заборонених символів
        parts = [p for p in re.split(r'[\\/]+', folder_name) if p not in ("", ".")]
        if not parts:
            parts = ["! ПЕРЕНАПРАВЛЕННЯ"]

        clean_parts = []
        for part in parts:
            part = part.strip(".,?:;()[]{}- ")
            part = self._clean_string(part)
            if not part:
                part = "! ПЕРЕНАПРАВЛЕННЯ"
            clean_parts.append(part)

        path = os.path.join(self._parent_path, *clean_parts)
        os.makedirs(path, exist_ok=True)  # exist_ok=True - не дає програмі впасти, якщо папка вже є
        return path

    # ---------- Make file
    def make_note(self, content, file_name, folder_name="! ПЕРЕНАПРАВЛЕННЯ"):  # making note, time
        date = datetime.now().strftime("%d.%m.%y")
        time_now = datetime.now().strftime("%H-%M")
        now = datetime.now().strftime("%d-%m-%Y %H:%M")

        if not file_name or file_name.strip() == "" or file_name.strip() == ".":
            if not content or content.strip() == ".":
                file_name = f"zeroNote_{date}_{time_now}"
            else:
                first_word = content.split()[0]
                clean_word = first_word.strip(".,?:;()[]{}")
                if not clean_word:
                    clean_word = "note"
                file_name = f"{clean_word[:15]}_{date}"
        else:
            file_name = self._clean_string(file_name)

        folder_path = self.create_folder(folder_name)
        full_path = os.path.join(folder_path, f"{file_name}.md")

        with open(full_path, mode='a', encoding='utf-8') as file:
            file.write(f"## {now}\n---\n {content} ")
            print(f"Нотатку збережено у: {full_path}")
        return full_path

    def get_folders(self, folder_name=""):
        target_path = os.path.join(self._parent_path, folder_name or "")
        try:
            items = os.listdir(target_path)
            folders = [f for f in items if os.path.isdir(os.path.join(target_path, f))]
            return folders
        except Exception as e:
            print(f"Помилка при отриманні папок: {e}")
            return []

    def get_files(self, folder_name=""):
        folder_path = os.path.join(self._parent_path, folder_name or "")
        try:
            if not os.path.exists(folder_path):
                print(f"DEBUG: Папки не існує: {folder_path}")
                return []
            items = os.listdir(folder_path)
            files = [f for f in items if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.md')]
            return files
        except Exception as e:
            print(f"Error in get_files: {e}")
            return []

    def append_to_note(self, content, file_name, folder_name=""):
        folder_path = self.create_folder(folder_name)
        if not file_name.endswith('.md'):
            file_name += '.md'
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n" + content)
        return file_path

    # ---------- Read file
    def read_note(self, file_name, folder_name=""):
        if not file_name.endswith('.md'):
            file_name += '.md'
        folder_path = os.path.join(self._parent_path, folder_name or "")
        file_path = os.path.join(folder_path, file_name)

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    # ---------- photo
    def append_image_to_note(self, photo_path, file_name, folder_name="DUST", caption=""):
        photo_path, file_name, folder_name, caption = map(
            lambda x: str(x or ""), [photo_path, file_name, folder_name, caption]
        )

        try:
            file_name = file_name or "Unsorted_Photos"
            folder_name = folder_name or "DUST"

            folder_path = self.create_folder(folder_name)

            dust_path = os.path.join(self._parent_path, "DUST")
            os.makedirs(dust_path, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_ext = os.path.splitext(photo_path)[1] or ".jpg"
            photo_file_name = f"img_{timestamp}{original_ext}"
            final_photo_path = os.path.join(dust_path, photo_file_name)

            shutil.move(photo_path, final_photo_path)

            image_link = f"\n![[DUST/{photo_file_name}]]\n{caption}\n"

            if not file_name.endswith('.md'):
                file_name += '.md'

            target_note_path = os.path.join(folder_path, file_name)

            with open(target_note_path, 'a', encoding='utf-8') as f:
                f.write(image_link)

            return True
        except Exception as e:
            print(f"ПОМИЛКА В БЕКЕНДІ: {e}")
            raise e