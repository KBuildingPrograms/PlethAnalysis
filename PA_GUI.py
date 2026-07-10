from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pandastable import Table, TableModel
import pandas as pd
import PA_Class_Func as pa
import sys
import traceback
    
iter = 0
loading = 0

def loadingbar():
    global loading
    loading += 5

def update_iter():
    global iter
    iter += 1

def jump(hour,minute,second):
    global iter
    time = int(((hour*3600 - 3600) + (minute*60) + second)/10)
    iter = time

class PA_IntroWindow: #first window for taking the ascii file name
    def __init__(self,frame):
        self.window = frame #takes the universal Tk
        self.window.title("File Input") #names it after the section

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
            if self.file_var:
                new = Analysis_Window(self.file_var) #initiates the next window
            elif self.savefile_var:
                new = Analysis_Savefile(self.savefile_var)
        except Exception as e:
            print(e)
    def file_name(self):
        e = "" #to update error message
        try:
            # skiprows = pa.skiprows(iter) #take the rows that are needed to skip based on the iteration at the time
            # _, _ = pa.signal_prep(self.file_var.get(),skiprows) #acquire the 20 second and 10 second interval
         
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


class Controls(Frame):
    def __init__(self, main):
        self.window = main.window
        control = main

        hour = iter//360 + 1
        minute = (iter - (hour-1)*360)//6
        second = iter - (hour-1)*360 - (minute*6)

        main.hour_var = IntVar(main.window, hour)
        main.minute_var = IntVar(main.window, minute)
        main.second_var = IntVar(main.window, second)

        H_entry = Entry(self.window, textvariable=main.hour_var, font=('calibre',12,'normal'))
        H_entry.place(relx=0.6, rely=0.8)
        M_entry = Entry(self.window, textvariable=main.minute_var, font=('calibre',12,'normal'))
        M_entry.place(relx=0.7, rely=0.8)
        S_entry = Entry(self.window, textvariable=main.second_var, font=('calibre',12,'normal'))
        S_entry.place(relx=0.8, rely=0.8)
        jump = Button(self.window, text='Jump',command=control.jumpto)
        jump.place(relx = 1.0, rely=0.8)

        next = Button(self.window, text="Next 10 Seconds", command=control.next_loop)
        next.place(relx=0.4,rely=0.75)

        refresh = Button(self.window, text="Refresh", command=control.summon_graph)
        refresh.place(relx=0.4,rely=0.7)

        save = Button(self.window, text="Save Progress", command=control.save)
        save.place(relx=0.9,rely=0.9)

        run_till = Button(self.window, text="Run till next detection", command=control.runtill)
        run_till.place(relx=0.4,rely=0.8)
        

class Analysis_Window:
    def __init__(self, filename):
        self.new_window(window) #makes a new window based off of the master Tk window
        self.width = self.window.winfo_width() #takes the width 
        self.height = self.window.winfo_height() #and height of the current window for future reference
        self.skiprows = pa.skiprows(iter)
        self.file_var = filename

        self.event_frame = Frame(self.window, width=int(self.width/3), height=int(self.height/4)) #frame for the list of all events
        self.events_dataframe = pd.DataFrame(columns=["Event","Start","Duration","Type","Questionable","Subapneas"])
        self.apneas = []
        self.sighs = []
        self.names = []
        self.starts = []
        self.durations = []
        self.types = []
        self.question = []
        self.subapneas = []

        self.hour_var = IntVar()
        self.minute_var = IntVar()
        self.second_var = IntVar()

        self.controls = Controls(self)

        self.acquire_data()
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatenate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()

    def new_window(self,frame):
        self.window = Toplevel(master=frame)
        self.window.title("AnalysisWindow")
        self.window.state('zoomed')
    def acquire_data(self):
        self.skiprows = pa.skiprows(iter) #take the rows that are needed to skip based on the iteration at the time
        self.main_data, self.subsection_data = pa.signal_prep(self.file_var.get(),self.skiprows) #acquire the 20 second and 10 second interval
    def analyze_data(self):
        self.peaks = pa.peak_analysis(self.subsection_data,(self.skiprows*(1/2000)))
        self.peaks_mean, self.peaks_area_mean = pa.peak_means(self.peaks)
        self.sighs = pa.find_sighs(self.peaks,self.peaks_mean,self.peaks_area_mean)
        for sigh in self.sighs or []:
                self.apneas = pa.postsigh_apnea(self.main_data,sigh)
        self.apneas = pa.type3_apnea(self.peaks, self.apneas)
        self.apneas = pa.apnea_combination(self.main_data,self.apneas)
    def concatenate_data(self):
        chunk_s = (sigh for sigh in self.sighs if self.subsection_data['Time'].iloc[0] < sigh.start_time < self.subsection_data['Time'].iloc[-1])
        chunk_a = (apnea for apnea in self.apneas if self.subsection_data['Time'].iloc[0] < apnea.start_time < self.subsection_data['Time'].iloc[-1])
        for sigh in chunk_s:
            self.names.append(sigh.name)
            self.starts.append(sigh.start_time)
            self.durations.append(sigh.duration)
            self.types.append("N/A")
            self.question.append(sigh.questionable)
            self.subapneas.append(sigh.sub_apneas)
        for apnea in chunk_a:
            self.names.append(apnea.name)
            self.starts.append(apnea.start_time)
            self.durations.append(apnea.duration[0])
            self.types.append(apnea.type)
            self.question.append("N/A")
            self.subapneas.append(apnea.sub_apneas)
        event_data = {"Event": self.names, "Start": self.starts, "Duration": self.durations, "Type": self.types, "Questionable": self.question, "Subapneas": self.subapneas}
        self.events_dataframe = pd.concat([self.events_dataframe,pd.DataFrame(data=event_data)]) 
    def display_events(self):
        self.event_table = Table(self.event_frame, dataframe=self.events_dataframe, showtoolbar=False, showstatusbar=True)
        self.event_frame.place(relx=0.0,rely=1.0,anchor="sw")
        self.event_table.update()
        self.event_table.show()
    def update_events(self):
        new = len(self.apneas) + len(self.sighs) - len(self.events_dataframe)
        print(new)
        new_events = self.events_dataframe.tail(new).copy()
        print(new_events)
        new_a = [pa.Apnea(row['Type'],row['Start'],row['Duration']) for _, row in new_events.iterrows() if row['Event'].upper()=='APNEA']
        new_s = [pa.Sigh(row['Start'],row['Duration']) for _, row in new_events.iterrows() if row['Event'].upper()=='SIGH']
        self.apneas.extend(new_a)
        self.sighs.extend(new_s)
    def summon_graph(self):
        self.update_events()
        fig = Figure(figsize=(14,4), dpi=110,linewidth=0.3)
        axes = fig.add_subplot()
        self.subsection_data.plot(x='Time',y='Flow',ax=axes,grid=True)
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        chunk_s = (sigh for sigh in self.sighs if self.subsection_data['Time'].iloc[0] < sigh.start_time < self.subsection_data['Time'].iloc[-1])
        chunk_a = (apnea for apnea in self.apneas if self.subsection_data['Time'].iloc[0] < apnea.start_time < self.subsection_data['Time'].iloc[-1])
        for sigh in chunk_s:
            axes.axvspan(sigh.start_time, sigh.width, alpha=0.3)
        for apnea in chunk_a:
            axes.axvspan(apnea.start_time, apnea.width, alpha=0.3, color='red')
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        toolbar.place(relx=0.5,rely=0.6,anchor='c')
        canvas.get_tk_widget().place(relx=0.5,rely=0.0,anchor="n")
    def next_loop(self):
        update_iter()
        self.acquire_data() #gets next ten seconds
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatenate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()
    def next_process(self):
        self.acquire_data()
        self.analyze_data()
        self.concatenate_data()
    def refresh(self):
        self.concatenate_data()
        self.display_events()
        self.summon_graph()
    def jumpto(self):
        jump(self.hour_var.get(),self.minute_var.get(),self.second_var.get())
        self.refresh()
    def runtill(self):
        current = len(self.events_dataframe)
        while len(self.events_dataframe) < current + 1:
            update_iter()
            self.next_process()
        self.refresh()
        
    def save(self):
        savefile_data = {"Filename": self.file_var.get(), "Current Iteration": iter, "Events": self.events_dataframe}
        savefile_dataframe = pd.DataFrame(savefile_data)
        savefile_dataframe.to_excel("savefile.xlsx")
        #sheet 1: current iteration, data filename/location
        #sheet 2: every sigh and apnea saved so far

#I think I'll make a second analysis window type for loading data

class Analysis_Savefile(Analysis_Window): #Moving some of the analysis methods to clean the window
    def acquire_data(self):
        global iter
        save_data = pd.read_excel(self.file_var.get())
        self.filename = save_data['Filename']
        iter = save_data["Current Iteration"].iloc[0]
        self.events_dataframe = save_data["Events"] #this is not the best way to do this lmao
        self.skiprows = pa.skiprows(iter)
        self.main_data, self.subsection_data = pa.signal_prep(self.filename,self.skiprows)
    def next_loop(self):
        super().next_loop()
    def refresh(self):
        super().refresh()
    def save(self):
        savefile_data = {"Filename": self.filename, "Current Iteration": iter, "Events": self.events_dataframe}
        savefile_dataframe = pd.DataFrame(savefile_data)
        savefile_dataframe.to_excel("savefile.xlsx")

    
        

        
window = Tk()
IntroWindow = PA_IntroWindow(window)
window.mainloop()





