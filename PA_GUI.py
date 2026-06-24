from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pandastable import Table, TableModel
import pandas as pd
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
iter = 0


class PA_IntroWindow:
    def __init__(self,frame,state):
        self.window = frame
        self.window.title("FirstStep")
        self.state = state
        self.iter = iter

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

            Analysis_Window(self.window,self.signal,self.sub_signal)
        except Exception as e:
            print("Invalid Filename")
            error_note = Label(self.window,text=e,font=('calibre',15,'bold'))
            error_note.grid(row=3,column=0)


class Analysis_Window:
    def __init__(self,window,dataframe, sub_dataframe):
        self.new_window(window)
        self.width = self.window.winfo_width()
        self.height = self.window.winfo_height()
        self.iter = iter

        self.window.title("Analysis")
        self.frame_table = Tk.Frame(self.window, width=int(self.width/2), height=self.height)
        self.main_data = dataframe
        self.subsection_data = sub_dataframe

        self.event_frame = Tk.Frame(self.windwo, width=int(self.width/2), height=int(self.height/2))
        self.display_data()
        self.analyze_data()
    def new_window(self,window):
        self.window = Toplevel(master=window)
        self.window.title = ("AnalysisWindow")
        self.window.attributes('-fullscreen',True)
    def display_data(self):
        self.table = Table(self.frame_table, dataframe=self.subsection_data, showtoolbar=True, showstatusbar=True)
        self.frame_table.place(relx=0.0,rely=0.0,anchor="nw")
        self.table.show()
    def analyze_data(self):
        self.peaks = pa.peak_analysis(self.sub_dataframe,self.iter)
        self.peaks_mean, self.peaks_area_mean = pa.peak_means(self.peaks)
        self.sighs = pa.find_sighs(self.peaks,self.peaks_mean,self.peaks_area_mean)
        self.apneas = pa.postsigh_apnea(self.main_data,self.sighs)
        self.apneas = pa.type3_apnea(self.peaks,self.apneas)
        self.apneas = pa.apnea_combination(self.main_data,self.apneas)
    def concatonate_data(self):
        names = []
        starts = []
        durations = []
        types = []
        question = []
        for sigh in self.sighs:
            names.append(sigh.name)
            starts.append(sigh.start)
            durations.append(sigh.duration)
            types.append("N/A")
            question.append(sigh.questionable)
        for apnea in self.apneas:
            names.append(apnea.name)
            starts.append(apnea.start)
            durations.append(apnea.duration)
            types.append(apnea.type)
            question.append("N/A")
        event_data = {"Event": names, "Start": starts, "Type": types, "Questionable": question}
        self.event_frame = pd.Dataframe(data=event_data)
    def display_events(self):
        self.event_table = Table(self.frame_frame, dataframe=self.event_frame, showtoolbar=True, showstatusbar=True)
        self.frame_table.place(relx=1.0,rely=1.0,anchor="se")
        self.table.show()

        

window = Tk()
IntroWindow = PA_IntroWindow(window,'zoomed')
window.mainloop()





