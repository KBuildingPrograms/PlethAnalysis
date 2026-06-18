from scipy import signal as scp
import matplotlib.pyplot as plt
import pandas as pd

class Apnea:
    def __init__(self,type,start_time,duration):
        self.duration = duration #need to update to fit list type 
        self.start_time = start_time
        self.type = type
    def __str__(self):
        return f"Duration: {self.duration}, Start: {self.start_time}, Type: {self.type}"
    def __repr__(self):
        return f"Duration: {self.duration}, Start: {self.start_time}, Type: {self.type}"
    
class Sigh:
    def __init__(self,start_time,duration):
        self.duration = duration
        self.start_time = start_time
        self.questionable = False
    def lack(self):
        self.questionable = True
    def __str__(self):
        #defining because it's useful for checking things
        return f"Duration: {self.duration}, Start: {self.start_time}"
    def __repr__(self):
        return f"Duration: {self.duration}, Start: {self.start_time}"

def skiprows():
    pass #getting prepared to make skipped rows updateable

def signal_prep(signal_name,skiprows):
    chunk_value = 20
    sampling_interval = 2000
    Nrows = chunk_value * sampling_interval #total number of rows
    if type(signal_name) is not str:
        raise TypeError("Signal name must be string") #guard against weird pass
    signal_name = signal_name.replace("\"","") #removes the windows quotations from copying 
    pleth_graph_ascii = signal_name 
    pleth_section = pd.read_csv(pleth_graph_ascii, sep="\\s+",index_col=False, skiprows=skiprows, nrows=Nrows, low_memory=False, header=0, names=["Time","Flow"])

    normalized_ps = pleth_section.copy()
    normalized_ps["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()

    pleth_ten_section = normalized_ps.head(len(normalized_ps) // 2).copy() 
    pleth_ten_section.plot(x="Time",y="Flow")

    return normalized_ps, pleth_ten_section

def peak_analysis(normalized_signal,skiprows):
    sampling_freq = 1/2000
    pts_peaks_tp = scp.find_peaks(normalized_signal["Flow"], height=1.1*normalized_signal['Flow'].std())
    pts_peaks_loc = pts_peaks_tp[0]*sampling_freq + skiprows
    pts_peaks_w =scp.peak_widths(normalized_signal["Flow"], pts_peaks_tp[0],rel_height=0.6)
    pts_peaks_height = pts_peaks_tp[1]["peak_heights"]
    pts_peaks_width = pts_peaks_w[0]*sampling_freq
    pts_peaks_start = pts_peaks_w[2]*sampling_freq + skiprows

    ptsp_data = {"Time": pts_peaks_loc, "Height": pts_peaks_height, "Width":pts_peaks_width, "Start": pts_peaks_start}
    ptsp_dataframe = pd.DataFrame(data=ptsp_data)
    return ptsp_dataframe

def peak_means(peak_data):
    ptsp_mean = peak_data['Height'].mean()
    ptsp_area_mean = peak_data['Width'].mean() * peak_data['Height'].mean()

    return ptsp_mean, ptsp_area_mean

def find_sighs(peak_dataframe,peak_height_mean,peak_area_mean): #i could add the peak stuff in here to really condense it 
    sighs = []
    for index, row in peak_dataframe.iterrows(): #going through all the peaks
        if row['Height'] > 1.25*peak_height_mean: #basis definition for a sigh
            if row['Width'] > 0.7*peak_area_mean: #other definition for a sigh
                new_sigh = Sigh(row['Start'],row['Width'])
                sighs.append[new_sigh]
    return sighs

def postsigh_apnea():
    #iterating through sighs
        #go ten seconds ahead, or to the next sigh
            #apnea?
                #yes
                    #how far after sigh?
                        #immediately
                            #add apnea, type 2
                        #took some time
                            #add apnea type 1
    pass

def type3_apnea():
        #iterating through peaks
        #same as in draft
    pass

def apnea_combination():
    #iterating through apneas
        #go ten seconds ahead, or to the next sigh
            #apnea?
                #yes
                    #already in list?
                        #yes
                            #add apnea's duration to the older one and remove it
                        #no
                            #add that apnea's duration to the old apnea in the iteration
    pass
