from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pandastable import Table, TableModel
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
        self.window.title("FirstStep")
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
        e = ""
        try:
            skiprows = pa.skiprows(self.iter)
            signal, sub_signal = pa.signal_prep(self.file_var.get(),skiprows)
            self.signal = signal
            self.sub_signal = sub_signal

            error_note = Label(self.window,text=e,font=('calibre',15,'bold'))
            error_note.grid(row=3,column=0)

            file_acq = Label(self.window,text='File Acquired!',font=('calibre',15,'bold'))
            file_acq.grid(row=3,column=0)
        except Exception as e:
            print("Invalid Filename")
            error_note = Label(self.window,text=e,font=('calibre',15,'bold'))
            error_note.grid(row=3,column=0)

class Analysis_Window:
    def __init__(self, root, dataframe, sub_dataframe):
        self.window = root
        self.window.attributes('-fullscreen', True)
        self.width = self.window.winfo_width()
        self.height = self.window.winfo_height()

        self.window.title("Analysis")
        self.frame_table = Tk.Frame(self.window, width=int(self.width/2), height=self.height)

        self.main_data = dataframe
        self.subsection_data = sub_dataframe
    def display_data(self):
        self.table = Table(self.frame_table, dataframe=self.subsection_data, showtoolbar=True, showstatusbar=True)
        self.table.show()
        #WIP
        pass
        
      
window = Tk()
IntroWindow = PA_IntroWindow(window,'zoomed')
window.mainloop()





