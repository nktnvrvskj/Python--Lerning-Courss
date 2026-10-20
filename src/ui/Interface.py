import tkinter as tk

from PIL import Image, ImageTk
from pathlib import Path

from logger import name_file
from ui.Frame import AppFrame
from ui.Button import AppButton

class Interface:
    def __init__(self,windows_w=400,windows_h=400):
        self.root = tk.Tk()

        self.root_w = windows_w
        self.root_h = windows_h

        self.root.geometry(f"{self.root_h}x{self.root_w}")

        icon_path = Path(__file__).parent.parent/".."/ "assets" / "icon.ico"
        img = Image.open(icon_path)
        icon = ImageTk.PhotoImage(img)

        self.frame = {}
        self.buttons = {}

        self.root.iconphoto(True, icon)

        self.create_interface()

        self.root.mainloop()

    def create_interface(self):
        self.create_frames(["menu", "task"])
        self.create_buttons(["menu", "task"],
                                ["Посмотреть задачи", "Добавить задачу"],
                            [lambda : self.frame["menu"].hide(True),lambda :self.frame["task"].hide(False)])

    def create_frames(self, mane_frame):
        for i,r in enumerate(mane_frame):
            frame = AppFrame(self.root,"#000000",self.root_w, self.root_h)
            if r == "menu":
                frame.hide(False)
            self.frame[r] = frame
        print(self.frame)

    def create_buttons(self, mane_frame, text, comands):
        for frame_name, button_text, command in zip(
                mane_frame, text, comands
        ):
            button = AppButton(
                self.frame[frame_name],
                button_text,
                command
            )
            self.buttons[frame_name] = button
        print(self.buttons)