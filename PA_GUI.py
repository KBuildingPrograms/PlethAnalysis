from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pandastable import Table
import sys
import traceback
import PA_Class_Func as pa

class PA_IntroWindow: #first window for taking the ascii file name
    def __init__(self,frame):
        self.window = frame #takes the universal Tk
        self.window.title("File Input") #names it after the section

        message = "Welcome to the Plethysmography Analysis Beta Build. To begin take the ascii data (or preferably the parquet copy) and open it via file explorer or" \
        " paste the file location. Additionally, if you have a savefile you can do the same with it."
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

        self.open_explorer = Button(self.window, text='Open File Folder', command=self.file_selection)
        self.open_explorer.grid(row=3,column=0)
    def summon_window(self): #summons the next window
        try:
            if self.file is not None:
                new = Analysis_Window(self.file) #initiates the next window
            elif self.savefile:
                new = Analysis_Savefile(self.savefile)
        except Exception as e:
            print(e)
    def file_selection(self):
        fn =  askopenfilename()
        if ".xlsx" in fn:
            self.savefile = fn
        elif ".ascii" or ".parquet"in fn:
            self.file = fn
        else:
            pass
        self.summon_window()
    def file_name(self):
        e = "" #to update error message
        try:
            # skiprows = pa.skiprows(iter) #take the rows that are needed to skip based on the iteration at the time
            # _, _ = pa.signal_prep(self.file_var.get(),skiprows) #acquire the 20 second and 10 second interval
         
            error_note = Label(self.window,text=e,font=('calibre',15,'bold')) #removes the error note if there was a previous error
            error_note.grid(row=3,column=0)

            file_acq = Label(self.window,text='File Acquired!',font=('calibre',15,'bold')) #alerts the user that the file name was functional
            file_acq.grid(row=3,column=0)
            self.savefile = self.savefile_var.get() if self.savefile_var.get() else None
            self.file = self.file_var.get() if self.file_var.get() else None
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

        hour = main.iter//360 + 1
        minute = (main.iter - (hour-1)*360)//6
        second = (main.iter - (hour-1)*360 - (minute*6))*10

        main.hour_var = IntVar(main.window, hour)
        main.minute_var = IntVar(main.window, minute)
        main.second_var = IntVar(main.window, second)

        H_entry = Entry(self.window, textvariable=main.hour_var, font=('calibre',12,'normal'))
        H_entry.place(relx=0.6, rely=0.6)
        M_entry = Entry(self.window, textvariable=main.minute_var, font=('calibre',12,'normal'))
        M_entry.place(relx=0.7, rely=0.6)
        S_entry = Entry(self.window, textvariable=main.second_var, font=('calibre',12,'normal'))
        S_entry.place(relx=0.8, rely=0.6)
        jump = Button(self.window, text='Jump',command=control.jumpto)
        jump.place(relx = 0.8, rely=0.65)

        next = Button(self.window, text="Next 10 Seconds", command=control.next_loop)
        next.place(relx=0.42,rely=0.65)

        refresh = Button(self.window, text="Refresh", command=control.refresh)
        refresh.place(relx=0.42,rely=0.7)

        save = Button(self.window, text="Save Progress", command=control.save)
        save.place(relx=0.9,rely=0.9)

        run_till = Button(self.window, text="Run till next detection", command=control.runtill)
        run_till.place(relx=0.42,rely=0.75)

        add = Button(self.window, text="Add Event", command=main.get_event)
        add.place(relx=0.42,rely=0.8)

        remove = Button(self.window, text="Remove Event", command=main.removal_loc)
        remove.place(relx=0.42, rely=0.85)

        edit = Button(self.window, text="Edit Event", command=main.edit_loc)
        edit.place(relx=0.42, rely=0.9)

        if main.total is not None:
            run_through = Button(self.window,text="Run Through",command=main.runthrough)
            run_through.place(relx=0.42,rely=0.95)

    def update_time(self, main):
        hour = main.iter//360 + 1
        minute = (main.iter - (hour-1)*360)//6
        second = (main.iter - (hour-1)*360 - (minute*6))*10

        main.hour_var.set(hour)
        main.minute_var.set(minute)
        main.second_var.set(second)

    def add_info(self,main):
        events = ['Sigh','Apnea','None']
        cb = ttk.Combobox(self.window, values=events)
        cb.set("Event")
        cb.place(relx=0.58,rely=0.8)

        start_var = DoubleVar(self.window)
        time_entry = Entry(self.window,textvariable=start_var,font=('calibre',12,'normal'))
        time_entry.place(relx=0.68,rely=0.8)

        duration_var = DoubleVar(self.window)
        duration_entry = Entry(self.window,textvariable=duration_var,font=('calibre',12,'normal'))
        duration_entry.place(relx=0.72,rely=0.8)

        types = ['1/2','3','N/A']
        cb_type = ttk.Combobox(self.window, values=types)
        cb_type.set("Type?")
        cb_type.place(relx=0.75,rely=0.8)

        sub_events = ['None']+main.apneas
        cb_subapnea = ttk.Combobox(self.window, values=sub_events)
        cb_subapnea.set("Sub Apbeas?")
        cb_subapnea.place(relx=0.85,rely=0.8)

        def submit():
            new_events = {'Apnea': pa.Apnea(cb_type.get(),start_var.get(),duration_var.get(),subapnea=[cb_subapnea.get()] if cb_subapnea.get() != 'None' else []), 'Sigh': pa.Sigh(start_var.get(),duration_var.get(),subapnea=[cb_subapnea.get()] if cb_subapnea.get() != 'None' else [])}
            main.input_event = new_events.get(cb.get(), None)
            main.add_event()
            cb.destroy()
            time_entry.destroy()
            duration_entry.destroy()
            cb_type.destroy()
            cb_subapnea.destroy()
            submit_button.destroy()
        def escape(event):
            cb.destroy()
            time_entry.destroy()
            duration_entry.destroy()
            cb_type.destroy()
            cb_subapnea.destroy()
            submit_button.destroy()
        
        self.window.bind('<Escape>', escape)
        submit_button = Button(self.window, text="Submit Event", command=submit)
        submit_button.place(relx=0.75,rely=0.85)
    def del_info(self, main):
        event_list = list(range(1,len(main.events_dataframe)+1))
        cb = ttk.Combobox(self.window, values=event_list)
        cb.set("Event to Delete")
        cb.place(relx=0.6, rely=0.8)
        def submit():
            loc = int(cb.get()) - 1
            main.event_loc = loc
            cb.destroy()
            submit_button.destroy()
            main.remove_event()
        def escape(event):
            cb.destroy()
            submit_button.destroy()
        
        self.window.bind('<Escape>', escape)
        submit_button = Button(self.window, text="Submit", command=submit)
        submit_button.place(relx=0.7, rely=0.8)
    def edit_info(self,main):
        event_list = main.events_dataframe.values.tolist()
        cb = ttk.Combobox(self.window, values=event_list)
        cb.set("Event to Edit")
        cb.place(relx=0.5, rely=0.9)
        def submit_loc():
            event_loc = cb.current() - 1
            event_edited = event_list[event_loc]
            cb.destroy()
            start_var = DoubleVar(self.window, value=event_edited[1])
            time_entry = Entry(self.window,textvariable=start_var,font=('calibre',12,'normal'))
            time_entry.place(relx=0.62,rely=0.8)

            duration_var = DoubleVar(self.window, value=event_edited[2])
            duration_entry = Entry(self.window,textvariable=duration_var,font=('calibre',12,'normal'))
            duration_entry.place(relx=0.65,rely=0.75)

            types = ['1/2','3','N/A']
            cb_type = ttk.Combobox(self.window, values=types)
            cb_type.set("Type?")
            cb_type.place(relx=0.7,rely=0.75)

            sub_events = main.apneas
            sub_events.insert(0,'')
            cb_subapnea = ttk.Combobox(self.window, values=sub_events)
            cb_subapnea.set("Sub Apbeas?")
            cb_subapnea.place(relx=0.75,rely=0.75)
            submit_button.destroy()
            def submit_edits():
                new_events = {'Apnea': pa.Apnea(cb_type.get(),start_var.get(),duration_var.get(),subapnea=[cb_subapnea.get()]), 'Sigh': pa.Sigh(start_var.get(),duration_var.get(),subapnea=[cb_subapnea.get()])}
                main.input_event = new_events.get(event_list[event_edited[0]], None)
                main.event_loc = event_loc
                main.edit_event()

                time_entry.destroy()
                duration_entry.destroy()
                cb_type.destroy()
                cb_subapnea.destroy()
                submit_edit_button.destroy()
            def escape2(event):
                cb.destroy()
                time_entry.destroy()
                duration_entry.destroy()
                cb_type.destroy()
                cb_subapnea.destroy()
                submit_edit_button.destroy()
            self.window.bind('<Escape>', escape2)
            submit_edit_button = Button(self.window, text="Submit Edits", command=submit_edits)
            submit_edit_button.place(relx=0.7, rely=0.9)
        def escape(event):
            cb.destroy()
            submit_button.destroy()
        
        self.window.bind('<Escape>', escape)
        submit_button = Button(self.window, text="Submit", command=submit_loc)
        submit_button.place(relx=0.7, rely=0.8)


    

class Analysis_Window:
    def __init__(self, filename):
        self.new_window(window) #makes a new window based off of the master Tk window
        self.width = self.window.winfo_width() #takes the width 
        self.height = self.window.winfo_height() #and height of the current window for future reference
        self.iter = 0
        self.skiprows = pa.skiprows(self.iter)
        self.filename = filename

        self.event_frame = Frame(self.window, width=int(self.width/3), height=int(self.height/4)) #frame for the list of all events
        self.events_dataframe = pa.pd.DataFrame(columns=["Event","Start","Duration","Type","Questionable","Subapneas"])

        self.total = None
        self.total_heightref = None
        self.input_event = None
        self.event_loc = None

        self.hour_var = IntVar()
        self.minute_var = IntVar()
        self.second_var = IntVar()

        

        self.acquire_data()
        self.controls = Controls(self)
        self.fig = Figure(figsize=(14,4), dpi=110,linewidth=0.3)
        self.axes = self.fig.add_subplot()
        self.analyze_data() #sends the 10 second interval through standard analysis
        #if self.total is not None: self.total_heightref = pa.total_deviation(self.total)
        #print(self.total_heightref)
        self.concatenate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()

    def new_window(self,frame):
        self.window = Toplevel(master=frame)
        self.window.title("AnalysisWindow")
        self.window.state('zoomed')
    def acquire_data(self):
        self.skiprows = pa.skiprows(self.iter) #take the rows that are needed to skip based on the iteration at the time
        if self.total is not None:
            self.main_data, self.subsection_data = pa.quick_prep(self.total,self.skiprows)
        else:
            self.total, self.main_data, self.subsection_data = pa.signal_prep(self.filename,self.skiprows) #acquire the 20 second and 10 second interval
    def analyze_data(self):
        self.sighs = pa.find_sighs(self.subsection_data,self.skiprows,self.total_heightref) 
        new_sigh = self.sighs[-1] if len(self.sighs) > 0 and (float(self.subsection_data['Time'].iloc[0]) < self.sighs[-1].start_time < float(self.subsection_data['Time'].iloc[-1])) else None
        self.apneas = pa.apnea_detection(self.main_data,self.subsection_data,self.skiprows,sigh=new_sigh)
        self.apneas = pa.apnea_detection(self.main_data,self.main_data.iloc[8*2000:12*2000],self.skiprows,sigh=new_sigh)
        self.apneas = pa.apnea_combination(self.main_data,self.skiprows,self.apneas)
    def concatenate_data(self):
        chunk_s = [sigh for sigh in self.sighs if self.subsection_data['Time'].iloc[0] < sigh.start_time < self.subsection_data['Time'].iloc[-1] and not pa.np.isclose(self.events_dataframe['Start'],sigh.start_time,atol=1e-5).any()]
        chunk_a = [apnea for apnea in self.apneas if self.subsection_data['Time'].iloc[0] < apnea.start_time < self.subsection_data['Time'].iloc[-1] and not pa.np.isclose(self.events_dataframe['Start'],apnea.start_time,atol=1e-5).any()]
        new_events = chunk_s + chunk_a
        for event in new_events:
            self.events_dataframe = pa.pd.concat([self.events_dataframe,pa.pd.DataFrame({'Event':[event[0]],'Start':[event[1]],'Duration':[event[2]],'Type':[event[3]],'Questionable':[event[4]],'Subapneas':[event[5]]})],ignore_index=True)
    def display_events(self):
        self.event_table = Table(self.event_frame, dataframe=self.events_dataframe, showtoolbar=False, showstatusbar=True)
        self.event_frame.place(relx=0.0,rely=1.0,anchor="sw")
        self.event_table.update()
        self.event_table.show()
    def update_events(self):
        new = len(self.apneas) + len(self.sighs) - len(self.events_dataframe)
        new_events = self.events_dataframe.tail(new).copy()
        new_a = [pa.Apnea(row.Type,row.Start,row.Duration) for row in new_events.itertuples() if row.Event.upper()=='APNEA']
        new_s = [pa.Sigh(row.Start,row.Duration) for row in new_events.itertuples() if row.Event.upper()=='SIGH']
        self.apneas.extend(new_a)
        self.sighs.extend(new_s)
    def get_event(self):
        self.controls.add_info(self)
    def add_event(self):
        if isinstance(self.input_event, pa.Apnea):
            self.apneas.append(self.input_event)
        elif isinstance(self.input_event, pa.Sigh):
            self.sighs.append(self.input_event)
        else:
            pass
        self.concatenate_data()
        self.input_event = None
    def removal_loc(self):
        self.controls.del_info(self)
    def remove_event(self):
        key_s = [sigh for sigh in self.sighs if self.events_dataframe['Start'].iloc[self.event_loc] == sigh.start_time]
        key_a = [apnea for apnea in self.apneas if self.events_dataframe['Start'].iloc[self.event_loc] == apnea.start_time]
        if key_a:
            self.apneas.pop(self.apneas.index(key_a[0]))
        if key_s:
            self.sighs.pop(self.apneas.index(key_s[0]))
        self.events_dataframe.drop([self.event_loc])
        self.event_loc = None
        self.display_events()
        self.refresh()
    def edit_loc(self):
        self.controls.edit_info(self)
    def edit_event(self):
        old_a = [apnea for apnea in self.apneas if self.events_dataframe['Start'].iloc[self.event_loc] == apnea.start_time]
        old_s = [sigh for sigh in self.sighs if self.events_dataframe['Start'].iloc[self.event_loc] == sigh.start_time]
        if old_a:
            pa.editinlists(old_a[0], self.events_dataframe)
            inner_index = self.apneas.index(old_a[0]) 
            self.apneas.pop(inner_index)
            self.apneas.insert(inner_index)
        if old_s:
            pa.editinlists(old_s[0], self.events_dataframe)
            inner_index = self.sighs.index(old_s[0]) 
            self.sighs.pop(inner_index)
            self.sighs.insert(inner_index)
        self.event_loc = None
        self.input_event = None
    def summon_graph(self):
        self.axes.clear()
        self.subsection_data.plot(x='Time',y='Flow',ax=self.axes,grid=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        chunk_s = (sigh for sigh in self.sighs if self.subsection_data['Time'].iloc[0] < sigh.start_time < self.subsection_data['Time'].iloc[-1])
        chunk_a = (apnea for apnea in self.apneas if self.subsection_data['Time'].iloc[0] < apnea.start_time < self.subsection_data['Time'].iloc[-1])
        for sigh in chunk_s:
            self.axes.axvspan(sigh.start_time, sigh.width, alpha=0.3)
            for apnea in sigh.sub_apneas:
                self.axes.axvspan(apnea.start_time, apnea.width, alpha=0.3, color='cyan')
        for apnea in chunk_a:
            self.axes.axvspan(apnea.start_time, apnea.width, alpha=0.3, color='red')
            for subapnea in apnea.sub_apneas:
                self.axes.axvspan(subapnea.start_time, subapnea.width, alpha=0.3, color='cyan')
        toolbar = NavigationToolbar2Tk(self.canvas, self.window)
        toolbar.update()
        toolbar.place(relx=0.5,rely=0.6,anchor='c')
        self.canvas.get_tk_widget().place(relx=0.5,rely=0.0,anchor="n")
    def reset(self):
        self.iter = 0 
    def update_iter(self):
        self.iter += 1
    def jump(self):
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        second = self.second_var.get()
        self.iter = int(((hour*3600 - 3600) + (minute*60) + second)/10)
    def next_loop(self):
        self.update_iter()
        self.acquire_data() #gets next ten seconds
        self.analyze_data() #sends the 10 second interval through standard analysis
        self.concatenate_data()
        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()
        self.controls.update_time(self)
    def next_process(self):
        self.acquire_data()
        self.analyze_data()
        self.concatenate_data()
    def refresh(self):
        self.display_events()
        self.summon_graph()
        self.controls.update_time(self)
    def jumpto(self):
        self.jump(self.hour_var.get(),self.minute_var.get(),self.second_var.get())
        self.concatenate_data()
        self.refresh()
    def runtill(self):
        current = len(self.events_dataframe)
        while len(self.events_dataframe) < current + 1:
            self.update_iter()
            self.next_process()
        self.refresh()
    def runthrough(self):
        self.save()
        if self.savefile_path:
            plt.close(self.fig)
            self.events_dataframe = pa.large_data_process(self.total,self.iter,self.total_heightref)
            print(self.events_dataframe)
            self.updatesave()
    def save(self):
        savefile_data = {"Filename": [self.filename], "Current Iteration": [self.iter]}
        savefile_dataframe = pa.pd.DataFrame(data=savefile_data)
        self.savefile_path = asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel Workbook","*.xlsx")],title="Save Your Document As")
        if self.savefile_path:
            with pa.pd.ExcelWriter(self.savefile_path, engine='xlsxwriter') as writer:
                savefile_dataframe.to_excel(writer,sheet_name='SaveState',index=False)
                self.events_dataframe.to_excel(writer,sheet_name='SavedEvents',index=False)
    def updatesave(self):
        print("Updated savefile!")
        savefile_data = {"Filename": [self.filename], "Current Iteration": [self.iter]}
        savefile_dataframe = pa.pd.DataFrame(data=savefile_data)
        with pa.pd.ExcelWriter(self.savefile_path, engine='xlsxwriter') as writer:
            savefile_dataframe.to_excel(writer,sheet_name='SaveState',index=False)
            self.events_dataframe.to_excel(writer,sheet_name='SavedEvents',index=False)



class Analysis_Savefile(Analysis_Window): #Moving some of the analysis methods to clean the window
    def __init__(self,filename):
        self.file_var = filename
        self.acquire_savedata()
        self.new_window(window) #makes a new window based off of the master Tk window
        self.width = self.window.winfo_width() #takes the width 
        self.height = self.window.winfo_height() #and height of the current window for future reference
        self.event_frame = Frame(self.window, width=int(self.width/3), height=int(self.height/4)) #frame for the list of all events
        
        self.apneas = pa.frametoapnea(self.events_dataframe)
        self.sighs = pa.frametosighs(self.events_dataframe)

        self.total = None
        self.input_event = None
        self.event_loc = None

        self.hour_var = IntVar()
        self.minute_var = IntVar()
        self.second_var = IntVar()

        self.controls = Controls(self)

        self.display_events() #display the list of events from the events dataframe
        self.summon_graph()
    def acquire_savedata(self):
        save_data = pa.pd.read_excel(self.file_var.get(),sheet_name=0)
        self.events_dataframe = pa.pd.read_excel(self.file_var.get(),sheet_name=1)
        self.filename = save_data['Filename'].iloc[0]
        self.iter = save_data["Current Iteration"].iloc[0]
        self.skiprows = pa.skiprows(self.iter)
        self.main_data, self.subsection_data = pa.signal_prep(self.filename,self.skiprows)
    def save(self):
        savefile_data = {"Filename": [self.filename], "Current Iteration": [self.iter]}
        savefile_dataframe = pa.pd.DataFrame(data=savefile_data)
        self.savefile_path = asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel Workbook","*.xlsx")],title="Save Your Document As")
        if self.savefile_path:
            with pa.pd.ExcelWriter(self.savefile_path, engine='xlsxwriter') as writer:
                savefile_dataframe.to_excel(writer,sheet_name='SaveState',index=False)
                self.events_dataframe.to_excel(writer,sheet_name='SavedEvents',index=False)
    def updatesave(self):
        savefile_data = {"Filename": [self.filename], "Current Iteration": [self.iter]}
        savefile_dataframe = pa.pd.DataFrame(data=savefile_data)
        with pa.pd.ExcelWriter(self.savefile_path, engine='xlsxwriter') as writer:
            savefile_dataframe.to_excel(writer,sheet_name='SaveState',index=False)
            self.events_dataframe.to_excel(writer,sheet_name='SavedEvents',index=False)
    
        

        
window = Tk()
IntroWindow = PA_IntroWindow(window)
window.mainloop()






