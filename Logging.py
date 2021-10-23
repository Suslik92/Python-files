from tkinter import Label, StringVar, Tk

from transitions import Machine

win = Tk()
intvar = StringVar()  # A tkinter string variable for labels
cntdwn = 10
intvar.set = 10


class Identification(object):
    def on_enter_A(self):
        print("We've just entered State A")
        update_window("System Started")

    def on_enter_B(self):
        print("We've just entered State B")
        update_window("Please look into the camera")

    def on_enter_C(self):
        print("We've just entered State C")
        update_window("Face and readings authorized")


def update_window(msg):
    label.configure(text=msg)


def rdy():
    # label= Label(win, text= "Sensors fully calibrated, please blow on the sensor", font=('Times New Roman bold',50))
    label.pack(padx=10, pady=10)
    label.configure(text="Sensors fully calibrated, please blow on the sensor")


def cntdwn_update(secs):
    if secs:
        label.configure(
            text="Greetings,booting system & calibrating sensors " + str(secs)
        )
        win.after(100, cntdwn_update, secs - 1)


SBS = Identification()
states = ["A", "B", "C"]  # Set the states in which the machine operates
transitions = [
    {"trigger": "System_Ready", "source": "A", "dest": "B"},
    {"trigger": "Picture_Taken", "source": "B", "dest": "C"},
    {"trigger": "User_Verified", "source": "C", "dest": "A"},
]  # Sets the transition parameter string for each state
machine = Machine(SBS, states=states, transitions=transitions, initial="A")

win.geometry("650x250")  # Set the geometry
win.attributes("-fullscreen", True)  # Create a fullscreen window
intvar.set = "Greetings, calibrating sensor (10s)"
label = Label(
    win,
    text="Greetings, calibrating sensors " + str(cntdwn),
    font=("Times New Roman bold", 50),
)
label.pack(padx=10, pady=10)
win.after(500, cntdwn_update, cntdwn - 1)
win.after(1000, rdy)
# win.after(12000, update_window, 'Please look into the camera')

win.after(2000, lambda: SBS.System_Ready())
win.after(3000, lambda: SBS.Picture_Taken())
win.after(4000, lambda: SBS.User_Verified())

print("Calling the main loop")
win.mainloop()
