from tkinter import *
from random import randint
root = Tk()
lab = Label(root)
lab.pack()

def update():
   lab['text'] = randint(0,1000)
   root.after(1000, update) # run itself again after 1000 ms

# run first time
update()

root.mainloop()