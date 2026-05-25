# PROTOTYPE 0.2

import os # operation system, manage folders and other

print("i work!")

class Obsidian_Note: 
    def __init__(self, path): # definition path
      if not path:
            raise ValueError("❌ path is not exist!")
      self._path = path  # here incapsulation for not change 
    
      
    def make_file(file): # open and edit files
      with open(mode='a', encoding = 'utf-8', newline=True) as f:
       print('\n', file=f)


path = r"G:\My Drive\NIX WORKSHOP"


# git add .                                   # Додає всі зміни
# git commit -m "new" 
# git push    