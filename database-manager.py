import json, os
import sqlalchemy
import tkinter as tk
import jsonStructure, env

class Window(tk.Tk):
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    jsonPath = os.path.join(scriptPath, 'json')
    os.makedirs(jsonPath, exist_ok=True)

    def __init__(self):
        super().__init__()
        self.initializeJsonFiles()

    def initializeJsonFiles(self):
        for table, structure in jsonStructure.JSON_FILES.items():
            if not os.path.isfile(f'{self.jsonPath}/{table}.json'):
                with open(f'{self.jsonPath}/{table}.json', 'w') as file:
                    json.dump(structure, file, indent=2)
        
if __name__ == '__main__':
    window = Window()
    window.mainloop()