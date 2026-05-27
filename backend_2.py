# PROTOTYPE 0.2

import os # operation system, manage folders and other

print("i work!")

class Obsidian_Note: 
    def __init__(self, path): # definition path
      if not path:
            raise ValueError("❌ path is not exist!")
      self._path = path  # here incapsulation for not change 
    
    os.makedirs("dir", exist_ok = True)
    def make_file(self, file_name): # open and edit files
        file_name = print("file name? :    ")
        full_path = os.path.join(self._path, file_name)

        if not file_name:
           file_name = "file_obs"
        with open(file_name, mode='a', encoding = 'utf-8', newline='') as f:
         print('', file=f)
        print("sucsess")


path = r"G:\My Drive\NIX WORKSHOP"

# python backend_2.py
# git add .                                   # Додає всі зміни
# git commit -m "new" 
# git push    