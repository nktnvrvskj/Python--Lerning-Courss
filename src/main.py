import tkinter as tk
from ui.Interface import Interface

from PIL import Image, ImageTk
from pathlib import Path

from storege import *
from config import NAME_FILES_SAVES


class App(Interface):
    def __init__(self, windows_w=400, windows_h=400):
        self.collection = load([], NAME_FILES_SAVES)
        self.root = tk.Tk()
        self.root_w = windows_w
        self.root_h = windows_h

        self.frame = {}
        self.buttons = {}

        self.root.geometry(f"{self.root_w}x{self.root_h}")

        icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        img = Image.open(icon_path)
        icon = ImageTk.PhotoImage(img)

        self.root.iconphoto(True, icon)

        super().__init__(self.root, self.frame, self.buttons)

        self.create_interface()
        self.add_listBox("task")
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.show_all_tasks()

        self.root.mainloop()

    def on_select(self, event):
        selection = self.listbox.curselection()
        print(self.collection[selection[0]])

    def show_all_tasks(self):
        for number, content in enumerate(self.collection):
            self.listbox.insert_list(content["name"])





App()