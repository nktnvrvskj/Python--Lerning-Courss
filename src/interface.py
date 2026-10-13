import tkinter as tk
score = 0

def start(id:int):
    print(id)
    global score
    score +=1
    label.config(text=score)
root = tk.Tk()
root.geometry("500x500")

Button = tk.Button(root,text="start", command=lambda: start(12))
Button.pack()
heder = tk.Frame(root, bg="light blue",height=400, width=400)
heder.pack(side="top",fill="x")
footer = tk.Frame(root, bg="light blue",height=400, width=400)
footer.pack(side="bottom",fill="x")
main = tk.Frame(root, bg="light blue",height=400, width=400)
main.pack(side="bottom",fill="x")


label= tk.Label(heder,text=0,height=20,width=50)
label.pack()

root.mainloop()
