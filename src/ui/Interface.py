import tkinter as tk

from logger import name_file
from ui.Frame import AppFrame
from ui.Button import AppButton
from ui.Listbox import AppListbox

class Interface:
    def __init__(self,root,frame,buttons):

        self.root =root
        self.frame = frame
        self.buttons = buttons

        self.listbox = tk.Listbox()

    def create_interface(self):
        self.create_frames(["menu", "task"])
        self.create_buttons(["menu", "task"],
                                ["Посмотреть задачи", "Добавить задачу"],
                            [lambda : (self.frame["menu"].hide(True),self.frame["task"].hide(False)),
                                        lambda :(self.frame["task"].hide(True),self.frame["menu"].hide(False))])

    def create_frames(self, mane_frame):
        for i,r in enumerate(mane_frame):
            frame = AppFrame(self.root,"#000000",self.root_w, self.root_h)
            if r == "menu":
                frame.hide(False)
            self.frame[r] = frame
        print(self.frame)

    def create_buttons(self, name_frame, text, comands):
        for frame_name, button_text, command in zip(
                name_frame, text, comands
        ):
            button = AppButton(
                self.frame[frame_name],
                button_text,
                command
            )
            self.buttons[frame_name] = button
        print(self.buttons)

    def add_listBox(self,name_frame):
        lb = AppListbox(self.frame[name_frame])
        self.listbox = lb