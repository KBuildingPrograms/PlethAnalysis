from scipy import signal as scp
import pandas as pd
import polars as pl
import numpy as np
cimport numpy as np

class Apnea:
    def __init__(self,a_type,start_time,duration,subapnea=None):
        cdef char self.name, self.type
        cdef double self.duration, self.start_time, self.width
        self.name = "Apnea"
        self.duration = duration #list of durations for the apneas
        self.start_time = start_time #the start of the first major apnea
        self.width = start_time + duration
        self.type = a_type #the type of the apnea (sighless type 3 or postsigh type 1/2)
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
        cdef char self.name
        cdef double self.duration, self.start_time, self.width
        cdef bool self.questionable
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
            new_apnea = Apnea(row.Type,float(row.Start),np.float32(row.Duration),subapnea=row.Subapneas)
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
    cdef int loc, start
    loc = (event_dataframe['Start'] == event.start_time).idxmax() if event.start_time in event_dataframe['Start'] else None
    start = 0
    if loc:
        for column in event_dataframe.iloc[loc]:
            event_dataframe[column].iloc[loc] = event[start]
            start += 1


cpdef int skiprows(iteration):
    cdef int skiprows, iteration
    skiprows = 2000*(3600 + iteration*10) #checks the iteration that we're on and takes the next 10 second chunk, always skips the first hour
    return skiprows

def signal_hour(signal_name,hour):
    cdef int sampling_interval, Nrows, total_seconds, skiprows
    dtypes = {'Time':pl.float32,'Flo':pl.float32}
    total_seconds = 3600
    sampling_interval = 2000
    Nrows = 2000*3600
    skiprows = 2000*(3600 + 3600*(hour-1))
    signal_name = signal_name.replace("\"","") #removes the windows quotations from copying 
    signal_name = signal_name.replace("\n","")
    hour_chunk = pl.read_csv(signal_name,has_header=False,skip_rows=skiprows,n_rows=Nrows,dtypes=dtypes)


def signal_prep(signal_name,skiprows):
    cdef int chunk_value, sampling_interval, Nrows
    chunk_value = 20 #block of time to take
    sampling_interval = 2000 #sampling freq
    Nrows = chunk_value * sampling_interval #total number of rows
    if type(signal_name) is not str:
        raise TypeError("Signal name must be string") #guard against weird pass
    signal_name = signal_name.replace("\"","") #removes the windows quotations from copying 
    signal_name = signal_name.replace("\n","")
    pleth_section = pl.read_parquet(signal_name,columns=["Time","Flow"],n_rows=Nrows+skiprows)
    return pleth_section 
    pleth_pandas = pleth_section.slice(skiprows, Nrows).to_pandas()
    #pleth_section = pd.read_csv(signal_name, sep="\\s+",index_col=False, skiprows=skiprows, nrows=Nrows, header=0, names=["Time","Flow"],engine='pyarrow')
        #^ converts ascii data to pd.dataframe
    normalized_signal = pleth_pandas.copy().astype('float32')
    normalized_signal["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()

    pleth_ten_section = normalized_signal.head(int(len(normalized_signal)*0.6)).copy() 

    return normalized_signal, pleth_ten_section

def peak_means(peak_data):
    ptsp_mean = peak_data['Height'].mean()
    ptsp_area_mean = peak_data['Width'].mean() * peak_data['Height'].mean()

    return ptsp_mean, ptsp_area_mean

def peak_analysis(normalized_signal,skiprows):
    cdef int skiprows
    cdef double sampling_freq
    sampling_freq = 1/2000
    pts_peaks_tp = scp.find_peaks(normalized_signal["Flow"], height=normalized_signal['Flow'].std())
    pts_inversepeaks = scp.find_peaks(-normalized_signal["Flow"], height=(-0.8)*normalized_signal['Flow'].std())
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
    cdef int skiprows
    cdef double height_margin, width_margin
    height_margin = 1.25
    width_margin = 0.7
    sighs = []
    peak_dataframe, inverse_data, peak_height_mean, peak_area_mean = peak_analysis(normalized_signal,skiprows)
    copy = peak_dataframe.copy()
    copy.sort_values(by=['Height'])
    row = copy.head(1).copy()
    inverse = [x for x in inverse_data if x > row['Start'].iloc[0]+row['Width'].iloc[0]]
    if row['Height'].iloc[0] > height_margin*peak_height_mean and row['Width'].iloc[0] > width_margin*peak_area_mean and inverse is not None:
                new_sigh = Sigh(row['Start'],row['Width'])
                sighs.append(new_sigh)
    return sighs

def apnea_detection(normalized_signal,normalized_subsection,skiprows,sigh=None):
    cdef int skiprows, I
    cdef char apneatype
    apneas = []
    i=0
    apneatype = "1/2" if sigh else "3"
    if sigh: 
        extended_view = normalized_signal.loc[(sigh.start_time < normalized_signal['Time']) & (normalized_signal['Time'] < sigh.start_time + 10), ['Time','Flow']]
    else:
        extended_view = normalized_subsection
    next_sigh = find_sighs(extended_view,skiprows)
    if len(next_sigh)>0: extended_view = extended_view.loc[extended_view['Time'] < next_sigh[0].start_time, ['Time','Flow']]
    extended_peaks, _, _, _ = peak_analysis(extended_view, skiprows)
    while i < len(extended_peaks) - 2:
        if extended_peaks["Start"].iloc[i+1] - (extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i]) > 0.7999:
            apnea = Apnea(apneatype,start_time=extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i],duration=extended_peaks["Start"].iloc[i+1] - (extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i]))
            if sigh: sigh.add_subapnea(apnea)
            apneas.append(apnea)
        i+=1
    if sigh and len(apneas) < 1: sigh.lack()
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
        end = sigh_caught[0].start_time if len(sigh_caught) > 0 else normalized_signal['Time'].loc[(normalized_signal['Time'] < apnea.start_time + 10)]
        for apnea2 in apneas: 
            if apnea.start_time < apnea2.start_time < end['Time'].iloc[-1]:
                apnea.add_subapnea(apnea2)
                removed_apneas.append(apnea2)

    apneas = [apnea for apnea in apneas if apnea not in removed_apneas]
    return apneas
