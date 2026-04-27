# this is a test for ObsidianNix Bot.I'm testing to open and write in local vaules.
# PROTOTYPE №1

from datetime import datetime #time
import os  #operation system


# for program can open files alone i need to show where and how she can do it?but how?

class ObsidianManager:
    def __init__(self, parent_path):
        #  here incapsulation for not change 
         self._parent_path = parent_path # Ми просто зберігаємо переданий шлях в self

    def create_folder(self, folder_name): #склеювання шляху,perent vault
            path = os.path.join(self._parent_path, folder_name)
            # Наприклад, те що ввів користувач:
    # exist_ok=True -  не дає програмі впасти, якщо папка вже є
            os.makedirs(path, exist_ok=True)
            return path

#  ----------Make file
    def make_note(self, content, folder_name = "! ПЕРЕНАПРАВЛЕННЯ", file_name = "newnote"):
         if not folder_name or folder_name.strip() == "":
            folder_name = "! ПЕРЕНАПРАВЛЕННЯ"
    
    # Те саме можна зробити для назви файлу
         if not file_name or file_name.strip() == "":
           file_name = "newnote"
         folder_path = self.create_folder(folder_name) #створення теки

         full_path = os.path.join(folder_path, f"{file_name}.md") #make them together


         now = datetime.now().strftime("%Y-%m-%d %H:%M")
         with open(full_path, mode = 'a',encoding='utf-8') as file:
              file.write(f"## {now}\n{content}\n\n---\n")
              print(f"Нотатку збережено у: {full_path}")

         return full_path
    

#     def list_folders(self):
#         # Цей метод покаже всі папки всередині Обсідіана
#         try:
#             items = os.listdir(self._parent_path)
#             # Фільтруємо тільки папки, ігноруємо системні файли
#             folders = [f for f in items if os.path.isdir(os.path.join(self._parent_path, f))]
#             return folders
#         except FileNotFoundError:
#             return "Помилка: Шлях не знайдено. Перевір адресу папки!"

# Заміни цей шлях на свій справжній шлях до Obsidian
parent_path = r"G:\My Drive\NIX WORKSHOπ" #! ПЕРЕНАПРАВЛЕННЯ

manager = ObsidianManager(parent_path)

# Отримуємо назву від користувача
folder  = input("Яку папку створити в Obsidian? ")
file_title = input("Назва файлу: ")
user_text = input("Текст нотатки: ")

manager.make_note(user_text, folder, file_title)