from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pandastable import Table, TableModel
import pandas as pd
import PA_Class_Func as pa
import sys
import traceback
    
iter = 0

def update():
    global iter
    iter += 1

class PA_IntroWindow: #first window for taking the ascii file name
    def __init__(self,frame):
        self.window = frame #takes the universal Tk
        self.window.title("File Input") #names it after the section
        self.iter = iter #takes the current iteration based on the global

        message = "Welcome to the Plethysmography Analysis Alpha Build. To begin take the ascii data of the plethysmography you want to analyze, remove the headers via notepad, and paste the file path below. Or, if you have a savefile with the place" \
        " you have so far, paste the file location of the savefile."
        t = Text(self.window, width=30, height=10, wrap='word',font=('calibre',12,'normal'))
        t.insert('1.0',message)
        t.grid(row=0,column=0)

        self.file_var = StringVar() #file name tkinter string
        self.file_label = Label(self.window,text="Paste Filename Here:",font=('calibre',15,'bold')) #prompts the user for the filename
        self.file_label.grid(row=1,column=0)
        self.file_entry = Entry(self.window, textvariable=self.file_var,font=('calibre',15,'normal')) #allows the user to enter the filename
        self.file_entry.grid(row=1,column=1)

        self.savefile_var = StringVar()
        self.savefile_label = Label(self.window,text="Paste Savefile Name Here:",font=('calibre',15,'bold'))
        self.savefile_label.grid(row=2,column=0)
        self.savefile_entry = Entry(self.window, textvariable=self.savefile_var,font=('calibre',15,'normal'))
        self.savefile_entry.grid(row=2,column=1)

        self.submit = Button(self.window, text="Submit", command=self.file_name) #submits the contents of the textbox to a section that may activate the next window
        self.submit.grid(row=3,column=1)
    def summon_window(self): #summons the next window
        try:
            new = Analysis_Window(self.file_var) #initiates the next window
        except Exception as e:
            print(e)
    def file_name(self):
        e = "" #to update error message
        try:
            skiprows = pa.skiprows(iter) #take the rows that are needed to skip based on the iteration at the time
            _, _ = pa.signal_prep(self.file_var.get(),skiprows) #acquire the 20 second and 10 second interval
         
            error_note = Label(self.window,text=e,font=('calibre',15,'bold')) #removes the error note if there was a previous error
            error_note.grid(row=3,column=0)

            file_acq = Label(self.window,text='File Acquired!',font=('calibre',15,'bold')) #alerts the user that the file name was functional
            file_acq.grid(row=3,column=0)
            
            self.summon_window() #if so, go to next window
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            tb_details = traceback.extract_tb(exc_tb)
            _, _, _, text = tb_details[-1]
            print(f"The error is: {text}") #to let me know what the error is while debugging
            error_note = Label(self.window,text=e,font=('calibre',15,'bold')) #informs the user what type of error ocurred while trying to load the file
            error_note.grid(row=3,column=0)



class Analysis_Window:
    def __init__(self, filename):
        self.new_window(window) #makes a new window based off of the master Tk window
        self.width = self.window.winfo_width() #takes the width 
        self.height = self.window.winfo_height() #and height of the current window for future reference
        self.skiprows = pa.skiprows(iter)
        self.file_var = filename

        self.frame_table = Frame(self.window, width=int(self.width/2), height=int(self.height/2)) #frame for the 10 second datatable that takes up about a half of the screen
        self.acquire_data()

        self.event_frame = Frame(self.window, width=int(self.width/3), height=int(self.height/3)) #frame for the list of all events
        self.apneas = []
        self.sighs = []
        self.names = []
        self.starts = []
        self.durations = []
        self.types = []
        self.question = []

        self.display_data() #displays the main data
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatonate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()

        next = Button(self.window, text="Next 10 Seconds", command=self.next_loop)
        next.place(relx=0.75,rely=0.75)
    def new_window(self,frame):
        self.window = Toplevel(master=frame)
        self.window.title("AnalysisWindow")
        self.window.state('zoomed')
    def acquire_data(self):
        self.skiprows = pa.skiprows(iter) #take the rows that are needed to skip based on the iteration at the time
        self.main_data, self.subsection_data = pa.signal_prep(self.file_var.get(),self.skiprows) #acquire the 20 second and 10 second interval
    def display_data(self):
        self.table = Table(self.frame_table, dataframe=self.subsection_data, showtoolbar=False, showstatusbar=True)
        self.frame_table.place(relx=0.0,rely=0.0,anchor="nw")
        self.table.update()
        self.table.show()
    def analyze_data(self):
        self.peaks = pa.peak_analysis(self.subsection_data,(self.skiprows*(1/2000)))
        self.peaks_mean, self.peaks_area_mean = pa.peak_means(self.peaks)
        self.sighs = pa.find_sighs(self.peaks,self.peaks_mean,self.peaks_area_mean)
        for sigh in self.sighs or []:
                self.apneas = pa.postsigh_apnea(self.main_data,sigh)
        self.apneas = pa.type3_apnea(self.peaks, self.apneas)
        self.apneas = pa.apnea_combination(self.main_data,self.apneas)
    def concatonate_data(self):
        for sigh in self.sighs:
            self.names.append(sigh.name)
            self.starts.append(sigh.start_time)
            self.durations.append(sigh.duration)
            self.types.append("N/A")
            self.question.append(sigh.questionable)
        for apnea in self.apneas:
            self.names.append(apnea.name)
            self.starts.append(apnea.start_time)
            self.durations.append(apnea.duration[0])
            self.types.append(apnea.type)
            self.question.append("N/A")
        event_data = {"Event": self.names, "Start": self.starts, "Duration": self.durations, "Type": self.types, "self.questionable": self.question}
        self.events_dataframe = pd.DataFrame(data=event_data)
    def display_events(self):
        self.event_table = Table(self.event_frame, dataframe=self.events_dataframe, showtoolbar=True, showstatusbar=True)
        self.event_frame.place(relx=0.0,rely=1.0,anchor="sw")
        self.event_table.update()
        self.event_table.show()
    def summon_graph(self):
        fig = Figure(figsize=(6.5,3.5), dpi=110)
        axes = fig.add_subplot()
        self.subsection_data.plot(x='Time',y='Flow',ax=axes)
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        for sigh in self.sighs:
            axes.axvspan(sigh.start_time, sigh.width, alpha=0.3)
        for apnea in self.apneas:
            axes.axvspan(apnea.start_time, apnea.width, alpha=0.3, color='red')
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        toolbar.place(relx=1.0,rely=0.5,anchor='e')
        canvas.get_tk_widget().place(relx=1.0,rely=0.0,anchor="ne")
    def next_loop(self):
        update()
        self.acquire_data() #gets next ten seconds
        self.display_data() #displays the main data
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatonate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()
        print(iter)
    def save(self):
        pass
        #sheet 1: current iteration, data filename/location
        #sheet 2: every sigh and apnea saved so far

#I think I'll make a second analysis window type for loading data


        
window = Tk()
IntroWindow = PA_IntroWindow(window)
window.mainloop()





