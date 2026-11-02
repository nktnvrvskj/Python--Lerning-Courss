import tkinter as tk

class AppListbox(tk.Listbox):
    def __init__(self, master):
        super().__init__(
            master
        )
        self.master = master
        self.pack()
    def insert_list(self,content):
        self.insert(tk.END, content)
    def delete_list(self):
        self.delete(0, tk.END)