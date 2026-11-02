from tkinter import *
import tkinter as tk

from ui.Interface import Interface
ui = Interface()
def init():
    print(collection)
    # tasks = tk.Listbox(frame_tasks, width=400, height=400)
    # tasks.pack()

def show():
    print(tasks.curselection())


#     tasks.delete(0, tk.END)
#     for tack in collection:
#         tasks.insert(tk.END, tack)
#
#
#
# def create_menu():
#     frame_memu.pack()
#     frame_tasks.pack_forget()




show_all_tasks()
ui.root.mainloop()
