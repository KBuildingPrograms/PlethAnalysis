from tkinter import *
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pandastable import Table, TableModel
import pandas as pd
import PA_Class_Func as pa
import sys
import traceback
    
iter = 0

def update():
    iter += 1

class PA_IntroWindow: #first window for taking the ascii file name
    def __init__(self,frame,state):
        self.window = frame #takes the universal Tk
        self.window.title("FirstStep") #names it after the section
        self.state = state #takes the condition that defines the window shape
        self.iter = iter #takes the current iteration based on the global

        self.file_var = StringVar() #file name tkinter string
        self.file_label = Label(self.window,text="Paste Filename Here:",font=('calibre',15,'bold')) #prompts the user for the filename
        self.file_label.grid(row=0,column=0)
        self.file_entry = Entry(self.window, textvariable=self.file_var,font=('calibre',15,'normal')) #allows the user to enter the filename
        self.file_entry.grid(row=0,column=1)

        self.savefile_var = StringVar()
        self.savefile_label = Label(self.window,text="Paste Savefile Name Here:",font=('calibre',15,'bold'))
        self.savefile_label.grid(row=1,column=0)
        self.savefile_entry = Entry(self.window, textvariable=self.savefile_var,font=('calibre',15,'normal'))
        self.savefile_entry.grid(row=1,column=1)

        self.submit = Button(self.window, text="Submit", command=self.file_name) #submits the contents of the textbox to a section that may activate the next window
        self.submit.grid(row=2,column=1)
    def summon_window(self): #summons the next window
        try:
            new = Analysis_Window(self.signal,self.sub_signal) #initiates the next window
        except Exception as e:
            print(e)
    def file_name(self):
        e = "" #to update error message
        try:
            skiprows = pa.skiprows(self.iter) #take the rows that are needed to skip based on the iteration at the time
            signal, sub_signal = pa.signal_prep(self.file_var.get(),skiprows) #acquire the 20 second and 10 second interval
            self.signal = signal #signal is the 20 second interval
            self.sub_signal = sub_signal #subsignal is the 10 second interval

            error_note = Label(self.window,text=e,font=('calibre',15,'bold')) #removes the error note if there was a previous error
            error_note.grid(row=3,column=0)

            file_acq = Label(self.window,text='File Acquired!',font=('calibre',15,'bold')) #alerts the user that the file name was functional
            file_acq.grid(row=3,column=0)
            
            self.summon_window() #if so, go to next window
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            tb_details = traceback.extract_tb(exc_tb)
            filename, line_number, func_name, text = tb_details[-1]
            print(f"The error is: {text}") #to let me know what the error is while debugging
            error_note = Label(self.window,text=e,font=('calibre',15,'bold')) #informs the user what type of error ocurred while trying to load the file
            error_note.grid(row=3,column=0)



class Analysis_Window:
    def __init__(self, dataframe,sub_dataframe):
        self.new_window(window) #makes a new window based off of the master Tk window
        self.width = self.window.winfo_width() #takes the width 
        self.height = self.window.winfo_height() #and height of the current window for future reference
        self.skiprows = pa.skiprows(iter)

        self.frame_table = Frame(self.window, width=int(self.width/2), height=int(self.height/2)) #frame for the 10 second datatable that takes up about a half of the screen
        self.main_data = dataframe
        self.subsection_data = sub_dataframe

        self.event_frame = Frame(self.window, width=int(self.width/3), height=int(self.height/3)) #frame for the list of all events
        self.display_data() #displays the main data
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatonate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()
    def new_window(self,frame):
        self.window = Toplevel(master=frame)
        self.window.title("AnalysisWindow")
    def display_data(self):
        self.table = Table(self.frame_table, dataframe=self.subsection_data, showtoolbar=False, showstatusbar=True)
        self.frame_table.place(relx=0.0,rely=0.0,anchor="nw")
        self.table.show()
    def analyze_data(self):
        self.peaks = pa.peak_analysis(self.subsection_data,(self.skiprows*(1/2000)))
        self.peaks_mean, self.peaks_area_mean = pa.peak_means(self.peaks)
        self.sighs = pa.find_sighs(self.peaks,self.peaks_mean,self.peaks_area_mean)
        self.apneas = []
        for sigh in self.sighs:
            self.apneas += pa.postsigh_apnea(self.main_data,sigh)
        self.apneas = pa.type3_apnea(self.peaks, self.apneas)
        self.apneas = pa.apnea_combination(self.main_data,self.apneas)
    def concatonate_data(self):
        names = []
        starts = []
        durations = []
        types = []
        question = []
        for sigh in self.sighs:
            names.append(sigh.name)
            starts.append(sigh.start_time)
            durations.append(sigh.duration)
            types.append("N/A")
            question.append(sigh.questionable)
        for apnea in self.apneas:
            names.append(apnea.name)
            starts.append(apnea.start_time)
            durations.append(apnea.duration)
            types.append(apnea.type)
            question.append("N/A")
        event_data = {"Event": names, "Start": starts, "Type": types, "Questionable": question}
        self.events_dataframe = pd.DataFrame(data=event_data)
    def display_events(self):
        self.event_table = Table(self.event_frame, dataframe=self.events_dataframe, showtoolbar=True, showstatusbar=True)
        self.event_frame.place(relx=0.0,rely=1.0,anchor="sw")
        self.event_table.show()
    def summon_graph(self):
        fig = Figure(figsize=(5,4), dpi=100)
        self.subsection_data.plot(x='Time',y='Flow')
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        for sigh in self.sighs:
            fig.axes[0].axvspan(sigh.start_time, sigh.start_time + sigh.duration)
        for apnea in self.apneas:
            fig.axes[0].axvspan(apnea.start_time, apnea.start_time + apnea.duration[0])
        canvas.get_tk_widget.pack()
    def next_loop(self):
        update()
        self.display_data() #displays the main data
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatonate_data()
        self.display_events() #display the list of events from the events dataframe
        #self.summon_graph()
    def save(self):
        pass
        #sheet 1: current iteration, data filename/location
        #sheet 2: every sigh and apnea saved so far

#I think I'll make a second analysis window type for loading data


        
window = Tk()
IntroWindow = PA_IntroWindow(window,'zoomed')
window.mainloop()





