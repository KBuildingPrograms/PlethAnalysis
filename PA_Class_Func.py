from scipy import signal as scp
import polars as pl
import pandas as pd
import numpy as np
import tqdm

class Apnea:
    def __init__(self,type,start_time,duration,subapnea=None):
        self.name = "Apnea"
        self.duration = duration #list of durations for the apneas
        self.start_time = start_time #the start of the first major apnea
        self.width = start_time + duration
        self.type = type #the type of the apnea (sighless type 3 or postsigh type 1/2)
        self.sub_apneas = subapnea if subapnea is not None else []
        self.data = [self.name,self.start_time,self.duration,self.type,'N/A',self.sub_apneas]
    def add_subapnea(self,apnea):
        self.sub_apneas.append(apnea)
    def __str__(self): #information for use via print function
        return f"Type: {self.type}, Start: {self.start_time}, Duration: {self.duration}"
    def __repr__(self):
        return f"Type: {self.type}, Start: {self.start_time}, Duration: {self.duration}"
    def __gt__(self, apnea2):
        return self.start_time > apnea2.start_time or apnea2 in self.sub_apneas
    def __eq__(self,apnea2):
        return self.start_time == apnea2.start_time
    def __getitem__(self, key):
        self.data = [self.name,self.start_time,self.duration,self.type,'N/A',self.sub_apneas]
        return self.data[key]
    def __setitem__(self, index, value):
        self.data = [self.name,self.start_time,self.duration,self.type,'N/A',self.sub_apneas]
        self.data[index] = value


    
class Sigh:
    def __init__(self,start_time,duration,questionable=False,subapnea=None):
        self.name = "Sigh"
        self.duration = duration #duration of sigh based on width
        self.start_time = start_time #start of the sigh
        self.width = start_time + duration
        self.questionable = False if questionable is False else True #whether the sigh could or couldnot potentially be a sniff
        self.sub_apneas = subapnea if subapnea is not None else []
    def add_subapnea(self,apnea):
        self.sub_apneas.append(apnea)
    def lack(self):
        self.questionable = True #set when there's no apneas after and it may be just a sniff
    def __str__(self):
        #defining for print because it's useful for checking things
        return f"Start: {self.start_time}, Duration: {self.duration}"
    def __repr__(self):
        return f"Start: {self.start_time}, Duration: {self.duration}"
    def __eq__(self,sigh2):
        return self.start_time == sigh2.start_time
    def __getitem__(self, key):
        self.data = [self.name,self.start_time,self.duration,'N/A',self.questionable,self.sub_apneas]
        return self.data[key]
    def __setitem__(self, index, value):
        self.data = [self.name,self.start_time,self.duration,'N/A',self.questionable,self.sub_apneas]
        self.data[index] = value

def signaltonoise(a, apnea=None, axis=0, ddof=0):
    b = a.loc[(apnea.start_time < a['Time'])&(a['Time'] < apnea.width), ['Flow']] if apnea is not None else np.asanyarray(a['Flow'])
    b = np.asanyarray(b)
    m = b.mean(axis)
    sd = b.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

def frametoapnea(dataframe):
    apneas = []
    for row in dataframe.itertuples(index=False):
        if row.Event =='Apnea': 
            new_apnea = Apnea(row.Type,float(row.Start),np.float64(row.Duration),subapnea=row.Subapneas)
            apneas.append(new_apnea)
    return apneas

def frametosighs(dataframe):
    sighs = []
    for row in dataframe.itertuples(index=False):
        if row.Event =='Sigh': 
            new_sigh = Sigh(float(row.Start),np.float64(row.Duration),questionable=bool(row.Questionable == 'True'),subapnea=row.Subapneas)
            sighs.append(new_sigh)
    return sighs

            

def editinlists(event,event_dataframe):
    loc = (event_dataframe['Start'] == event.start_time).idxmax() if event.start_time in event_dataframe['Start'] else None
    start = 0
    if loc:
        for column in event_dataframe.iloc[loc]:
            event_dataframe[column].iloc[loc] = event[start]
            start += 1

def eventstoframe(current_frame,sighs=[],apneas=[]):
    total = sighs + apneas
    for event in total:
        eventframe = pd.DataFrame({'Event':[event[0]],'Start':[event[1]],'Duration':[event[2]],'Type':[event[3]],'Questionable':[event[4]],'Subapneas':[event[5]]})
        current_frame = pd.concat([current_frame,eventframe],ignore_index=True)
    return current_frame

def skiprows(iteration):
    skiprows = 2000*(3600 + iteration*10) #checks the iteration that we're on and takes the next 10 second chunk, always skips the first hour
    return skiprows

def signal_prep(signal_name,skiprows):
    chunk_value = 20 #block of time to take
    sampling_interval = 2000 #sampling freq
    Nrows = chunk_value * sampling_interval #total number of rows
    if type(signal_name) is not str:
        raise TypeError("Signal name must be string") #guard against weird pass
    signal_name = signal_name.replace("\"","") #removes the windows quotations from copying 
    signal_name = signal_name.replace("\n","")
    pleth_graph_ascii = signal_name #takes the ascii input data
    if ".parquet" in signal_name:
        total_pleth = pl.read_parquet(signal_name,columns=["Time","Flow"])
        pleth_section = total_pleth.slice(skiprows,Nrows).to_pandas()
    if ".ascii" in signal_name:
        total_pleth = None
        pleth_section = pd.read_csv(pleth_graph_ascii, sep="\\s+",index_col=False, skiprows=skiprows, nrows=Nrows, header=0, names=["Time","Flow"])
        #^ converts ascii data to pd.dataframe
    normalized_signal = pleth_section.copy().astype('float32')
    normalized_signal["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()

    pleth_ten_section = normalized_signal.head(int(len(normalized_signal)*0.6)).copy() 
    return total_pleth, normalized_signal, pleth_ten_section

def quick_prep(total_pleth,skiprows):
    chunk_value = 20 #block of time to take
    sampling_interval = 2000 #sampling freq
    Nrows = chunk_value * sampling_interval #total number of rows
    pleth_section = total_pleth.slice(skiprows,Nrows).to_pandas()
    normalized_signal = pleth_section.copy().astype('float32')
    normalized_signal["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()

    pleth_ten_section = normalized_signal.head(int(len(normalized_signal)*0.6)).copy() 
    return normalized_signal, pleth_ten_section

def total_deviation(total_data):
    total_data_peakref = total_data["Flow"].std()
    return total_data_peakref

def peak_means(peak_data):
    ptsp_mean = peak_data['Height'].mean()
    ptsp_area_mean = peak_data['Width'].mean() * peak_data['Height'].mean()

    return ptsp_mean, ptsp_area_mean

def peak_analysis(normalized_signal,skiprows):
    sampling_freq = 1/2000
    height = normalized_signal['Flow'].std() 
    pts_peaks_tp = scp.find_peaks(normalized_signal["Flow"], height=height*1.1)
    pts_inversepeaks = scp.find_peaks(-normalized_signal["Flow"], height=(-0.9)*height)
    pts_inversepeaks_loc = pts_inversepeaks[0]*sampling_freq + skiprows*sampling_freq
    pts_peaks_loc = pts_peaks_tp[0]*sampling_freq + skiprows*sampling_freq
    pts_peaks_w =scp.peak_widths(normalized_signal["Flow"], pts_peaks_tp[0],rel_height=0.6)
    pts_peaks_height = pts_peaks_tp[1]["peak_heights"]
    pts_peaks_width = pts_peaks_w[0]*sampling_freq
    pts_peaks_start = pts_peaks_w[2]*sampling_freq + skiprows*sampling_freq

    ptsp_data = {"Time": pts_peaks_loc, "Height": pts_peaks_height, "Width":pts_peaks_width, "Start": pts_peaks_start}
    ptsp_dataframe = pd.DataFrame(data=ptsp_data)
    

    ptsp_mean, ptsp_area_mean = peak_means(ptsp_dataframe)
    return ptsp_dataframe, pts_inversepeaks_loc, ptsp_mean, ptsp_area_mean

def find_sighs(normalized_signal,skiprows): #i could add the peak stuff in here to really condense it 
    sighs = []
    peak_dataframe, inverse_data, peak_height_mean, peak_area_mean = peak_analysis(normalized_signal,skiprows)
    copy = peak_dataframe.copy(deep=False)
    copy = copy.sort_values(by=['Height'],ascending=False)
    row = copy.head(1).copy()
    inverse = [x for x in inverse_data if x > row['Start'].iloc[0]+row['Width'].iloc[0]]
    if row['Height'].iloc[0] > 1.25*peak_height_mean and row['Width'].iloc[0] > 0.7*peak_area_mean and inverse is not None:
                new_sigh = Sigh(row['Start'].iloc[0],row['Width'].iloc[0])
                sighs.append(new_sigh)
    return sighs

def apnea_detection(normalized_signal,normalized_subsection,skiprows,sigh=None):
    apneas = []
    i=0
    if sigh: 
        extended_view = normalized_signal.loc[(normalized_signal['Time'] < sigh.start_time), ['Time','Flow']]
        next_view = normalized_signal.loc[(sigh.start_time < normalized_signal['Time']),['Time','Flow']]
        next_sigh = find_sighs(next_view,skiprows)
        if len(next_sigh)>0: next_view = next_view.loc[(next_view["Time"] < next_sigh[0]), ['Time','Flow']]
        new_peaks, _, _, _ = peak_analysis(next_view, skiprows)
        g = 0
        apneatype='1/2'
        while g < len(new_peaks) - 2:
            if new_peaks["Start"].iloc[i+1] - (new_peaks["Start"].iloc[i]+new_peaks["Width"].iloc[i]) > 0.7999:
                apnea = Apnea(apneatype,start_time=new_peaks["Start"].iloc[i]+new_peaks["Width"].iloc[i],duration=new_peaks["Start"].iloc[i+1] - (new_peaks["Start"].iloc[i]+new_peaks["Width"].iloc[i]))
                sigh.add_subapnea(apnea)
                apneas.append(apnea)
            g+=1
    else:
        extended_view = normalized_subsection
        next_view = None  
    apneatype = "3"
    extended_peaks, _, _, _ = peak_analysis(extended_view, skiprows)
    while i < len(extended_peaks) - 2:
        if extended_peaks["Start"].iloc[i+1] - (extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i]) > 0.7999:
            apnea = Apnea(apneatype,start_time=extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i],duration=extended_peaks["Start"].iloc[i+1] - (extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i]))
            apneas.append(apnea)
        i+=1
    return apneas


def matching_apnea(apnea,apneas):
    return any(
        apnea2.start_time == apnea #if there's another apnea that has the same start time as the input, return True
        for apnea2 in apneas
    )

def apnea_combination(normalized_signal,skiprows,apneas): #I need a way to clean this, good god
    removed_apneas = []
    for apnea in apneas:
        sigh_caught = find_sighs(normalized_signal,skiprows)
        end = sigh_caught[0].start_time if len(sigh_caught) > 0 else normalized_signal['Time'].loc[(normalized_signal['Time'] < apnea.start_time + 10)].iloc[-1]
        for apnea2 in apneas: 
            if apnea.start_time < apnea2.start_time < end:
                apnea.add_subapnea(apnea2)
                removed_apneas.append(apnea2)

    apneas = [apnea for apnea in apneas if apnea not in removed_apneas]
    return apneas


def large_data_process(total_data,iter):
    total_iter = 360+iter
    chunk_value = 20 #block of time to take
    sampling_interval = 2000 #sampling freq
    Nrows = chunk_value * sampling_interval #total number of rows
    events_container = pd.DataFrame(columns=["Event","Start","Duration","Type","Questionable","Subapneas"])
    with tqdm.tqdm(range(iter,total_iter)) as full_range:
        for i in full_range:
            skip_rows = skiprows(iter)
            pleth_section = total_data.slice(skip_rows,Nrows).to_pandas()
            pleth_section["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()
            pleth_ten_section = pleth_section.head(int(len(pleth_section)*0.6)).copy() 
            sigh_container = find_sighs(pleth_section,skip_rows)
            new_sigh = sigh_container[-1] if len(sigh_container) > 0 and pleth_ten_section['Time'].iloc[0] < sigh_container[-1].start_time < pleth_ten_section['Time'].iloc[-1] else None
            apnea_container = apnea_detection(pleth_section,pleth_ten_section,skip_rows,new_sigh)
            apnea_container = apnea_combination(pleth_section,skip_rows,apnea_container)
            eventstoframe(events_container,sigh_container,apnea_container)
    return events_container
    pass
