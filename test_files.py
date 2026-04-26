# this is a test for ObsidianNix Bot.I'm testing to open and write in local vaules.
# PROTOTYPE №1


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

    def list_folders(self):
        # Цей метод покаже всі папки всередині твого Обсідіана
        try:
            items = os.listdir(self.parent_path)
            # Фільтруємо тільки папки, ігноруємо системні файли
            folders = [f for f in items if os.path.isdir(os.path.join(self.parent_path, f))]
            return folders
        except FileNotFoundError:
            return "Помилка: Шлях не знайдено. Перевір адресу папки!"
#  ----------Make file
    def make_note(self,file_name,content):
         full_patch = os.path.join(self._parent_path, f"{file_name}.md") 
         with open(full_patch, mode = 'a',encoding='utf-8') as file:
              file.write(f"{content}/n")

         return full_patch
         
        
    
         

    
    # def write_note(self, folder_name, file_name, content):
    #     # Створюємо повний шлях до файлу
    #     folder_path = os.path.join(self.vault_path, folder_name)
    #     full_path = os.path.join(folder_path, f"{file_name}.md")

        # # Відкриваємо файл для допису (режим 'a' - append)
        # with open(full_path, 'a', encoding='utf-8') as file:
        #     file.write(f"\n{content}")
        # print(f"Нотатку збережено у: {full_path}")


# Заміни цей шлях на свій справжній шлях до Obsidian
parent_path = r"C:\Users\vasil\OneDrive\MYWORLD\! PROJECTS\obsidNix_Bot\TEST(DELETE.LATER)"

manager = ObsidianManager(parent_path)

# Отримуємо назву від користувача
user_choice = input("Яку папку створити в Obsidian? ")

# Передаємо цей вибір у метод класу
final_path = manager.create_folder(user_choice)

print(f"Готово! Папка лежить тут: {final_path}")

# manager = ObsidianManager(my_vault)
# folders = manager.list_folders()

# print("Твої папки в Obsidian:")
# for i, name in enumerate(folders):
#     print(f"{i+1}. {name}")