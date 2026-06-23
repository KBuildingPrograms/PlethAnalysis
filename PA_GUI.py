from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import PA_Class_Func as pa

def plot():
    pass
    #https://stackoverflow.com/questions/71815610/interactive-figures-in-tkinter
    # canvas - FigureCanvasTkAgg(fig,master=window)
    # canvas.draw()
    # canvas.get_tk_widget().pack()
    # toolbar = NaviagtionToolbar2Tk(canvas,window)
    # toolbar.update()
    # canvas.get_tk_widget().pack()

class PA_IntroWindow:
    def __init__(self,root,state):
        self.window = root
        self.title = "FirstStep"
        self.state = state
        self.iter = 0

        self.file_var = StringVar()
        self.file_label = Label(self.window,text="Paste Filename Here:",font=('calibre',15,'bold'))
        self.file_label.grid(row=0,column=0)
        self.file_entry = Entry(self.window, textvariable=self.file_var,font=('calibre',15,'normal'))
        self.file_entry.grid(row=0,column=1)
        self.submit = Button(self.window, text="Submit", command=self.file_name)
        self.submit.grid(row=2,column=1)

    def file_name(self):
        try:
            skiprows = pa.skiprows(self.iter)
            signal, sub_signal = pa.signal_prep(self.file_var.get(),skiprows)
            self.signal = signal
            self.sub_signal = sub_signal

            file_acq = Label(self.window,text='File Acquired!',font=('calibre',15,'bold'))
            file_acq.grid(row=3,column=0)
        except Exception as e:
            print("Invalid Filename")
            print(e)
        
      
window = Tk()
IntroWindow = PA_IntroWindow(window,'zoomed')
window.mainloop()





