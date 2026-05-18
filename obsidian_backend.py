# this is a test for ObsidianNix Bot.I'm testing to open and write in local vaules.
# PROTOTYPE №1

from datetime import datetime #time
import os  #operation system
import shutil


# for program can open files alone i need to show where and how she can do it?but how?

class ObsidianManager:
    def __init__(self, parent_path):
        #  here incapsulation for not change 
         self._parent_path = parent_path 
    def _clean_string(self, text):    #чистка заборонених символів   #можна було використати вбудований метод еее
        forbidden = r'\/:*?"<>|'
        for char in forbidden:
            text = text.replace(char, "")
        return text.strip()

    def create_folder(self, folder_name): # склеювання шляху,perent vault
          clean_name = self._clean_string(folder_name)
          path = os.path.join(self._parent_path, clean_name)
          os.makedirs(path, exist_ok=True)
          return path
         
    # exist_ok=True -  не дає програмі впасти, якщо папка вже є
            

#  ----------Make file
    def make_note(self, content,  file_name, folder_name = "! ПЕРЕНАПРАВЛЕННЯ",):
         date =  datetime.now().strftime("%d.%m.%y")
         time_now = datetime.now().strftime("%H-%M")     # час короче
         now = datetime.now().strftime("%d-%m-%Y %H:%M")


         if not folder_name or folder_name.strip() == "":
                folder_name = "! ПЕРЕНАПРАВЛЕННЯ"
         else:
            folder_name = folder_name.strip(".,?:;()[]{}-")

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
         full_path = os.path.join(folder_path, f"{file_name}.md") #make them together


         with open(full_path, mode = 'a',encoding='utf-8') as file:
              file.write(f"## {now}\n---\n {content} ")
              print(f"Нотатку збережено у: {full_path}")

         return full_path
    

    def get_folders(self):
        try:
            items = os.listdir(self._parent_path)
            folders = [f for f in items if os.path.isdir(os.path.join(self._parent_path, f))]
            return folders
        except FileNotFoundError:
            return []
    def get_files(self, folder_name=""):
        folder_path = os.path.join(self._parent_path, folder_name)
        try:
            items = os.listdir(folder_path)
            files = [f for f in items if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.md')]
            return files
        except FileNotFoundError:
            return []

    def append_to_note(self, content, file_name, folder_name=""):
        folder_path = os.path.join(self._parent_path, folder_name)
        if not file_name.endswith('.md'):
            file_name += '.md'
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n" + content)
        return file_path
    


    # photo
    def append_image_to_note(self, photo_path, file_name, folder_name="DUST", caption=""):
        try:
            # 1. Шлях до папки з ресурсами (завжди DUST)
            dust_path = os.path.join(self._parent_path, "DUST")
            os.makedirs(dust_path, exist_ok=True)

            # 2. Формуємо нове ім'я для фото (додаємо час, щоб імена не дублювалися)
            timestamp = datetime.now().strftime("%H%M%S")
            original_ext = os.path.splitext(photo_path)[1]
            photo_file_name = f"img_{timestamp}{original_ext}"
            final_photo_path = os.path.join(dust_path, photo_file_name)

            # 3. Переносимо фізичний файл у DUST
            shutil.move(photo_path, final_photo_path)

            # 4. Формуємо посилання для Obsidian
            image_link = f"\n![[{photo_file_name}]]\n{caption}\n"

            # 5. Дописуємо посилання у твій обраний файл
            if not file_name.endswith('.md'):
                file_name += '.md'
            
            target_path = os.path.join(self._parent_path, folder_name, file_name)
            
            with open(target_path, 'a', encoding='utf-8') as f:
                f.write(image_link)
            
            return True
        except Exception as e:
            print(f"Error in backend image append: {e}")
            raise e
 
parent_path = r"/mnt/g/My Drive/NIX WORKSHOP" #! ПЕРЕНАПРАВЛЕННЯ


"""test side"""

# manager = ObsidianManager(parent_path)

# folder  = input("Яку папку створити в Obsidian? ")
# file_title = input("Назва файлу: ")
# user_text = input("Текст нотатки: ")
