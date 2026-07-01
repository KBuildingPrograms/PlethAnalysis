from scipy import signal as scp
import pandas as pd

class Apnea:
    def __init__(self,type,start_time,duration):
        self.name = "Apnea"
        self.duration = duration #list of durations for the apneas
        self.start_time = start_time #the start of the first major apnea
        self.width = start_time + duration[0]
        self.type = type #the type of the apnea (sighless type 3 or postsigh type 1/2)
    def __str__(self): #information for use via print function
        return f"Duration: {self.duration}, Start: {self.start_time}, Type: {self.type}"
    def __repr__(self):
        return f"Duration: {self.duration}, Start: {self.start_time}, Type: {self.type}"
    
class Sigh:
    def __init__(self,start_time,duration):
        self.name = "Sigh"
        self.duration = duration #duration of sigh based on width
        self.start_time = start_time #start of the sigh
        self.width = start_time + duration
        self.questionable = False #whether the sigh could or couldnot potentially be a sniff
    def lack(self):
        self.questionable = True #set when there's no apneas after and it may be just a sniff
    def __str__(self):
        #defining for print because it's useful for checking things
        return f"Duration: {self.duration}, Start: {self.start_time}"
    def __repr__(self):
        return f"Duration: {self.duration}, Start: {self.start_time}"

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
    pleth_section = pd.read_csv(pleth_graph_ascii, sep="\\s+",index_col=False, skiprows=skiprows, nrows=Nrows, low_memory=False, header=0, names=["Time","Flow"])
        #^ converts ascii data to pd.dataframe
    normalized_signal = pleth_section.copy()
    normalized_signal["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()

    pleth_ten_section = normalized_signal.head(len(normalized_signal) // 2).copy() 
    pleth_ten_section.plot(x="Time",y="Flow")

    return normalized_signal, pleth_ten_section

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
                sighs.append(new_sigh)
    return sighs

def postsigh_apnea(normalized_signal, sigh):
    #iterating through sighs
    extended_view = normalized_signal.loc[(sigh.start_time < normalized_signal['Time']) & (normalized_signal['Time'] < sigh.start_time + 10), ['Time','Flow']] #extending 10 seconds out from sigh
    extended_peaks = peak_analysis(extended_view, extended_view['Time'].iloc[0]) #gets the peaks of that ten second interval
    extended_peak_hmean, extended_peak_amean = peak_means(extended_peaks)
    next_sigh = find_sighs(extended_peaks,extended_peak_hmean, extended_peak_amean) #if there's another sigh within ten seconds, catch it
    i=0 #indexing value for while loops
    apneas = [] #to acquire apneas
    if len(next_sigh) > 0: #if there is a sigh
        extended_peak_view = extended_peaks.loc[next_sigh[0].start_time > extended_view['Time']] #condense the extended peak view to end before the next sigh
        while i < len(extended_peak_view) - 2: #While the index is less than the maximum
            if extended_peak_view["Start"].iloc[i+1] - (extended_peak_view["Start"].iloc[i]+extended_peak_view["Width"].iloc[i]) > 0.7999:
                #if the distance between the start of the next peak and the end of the first peak is greater than 0.7999, that means there's an apnea
                apnea = Apnea("1/2", extended_peak_view["Start"].iloc[i] + extended_peak_view["Width"].iloc[i],[extended_peak_view["Start"].iloc[i+1] - (extended_peak_view["Start"].iloc[i] + extended_peak_view["Width"].iloc[i])])
                #the apnea is defined as type 1 or 2, starting at the end of the first peak, and has a duration from the end of the last peak to the start of the next, placed in a list so more duration can be added if needed
                apneas.append(apnea) #add the apnea to a list of apneas
            i+=1 #move on to next peak
    else:
        while i < len(extended_peaks) - 2:
            #same process but iterates from the sigh to 10 seconds after the sigh
            if extended_peaks["Start"].iloc[i+1] - (extended_peaks["Start"].iloc[i]+extended_peaks["Width"].iloc[i]) > 0.7999:
                apnea = Apnea("1/2", extended_peaks["Start"].iloc[i] + extended_peaks["Width"].iloc[i],[extended_peaks["Start"].iloc[i+1] - (extended_peaks["Start"].iloc[i] + extended_peaks["Width"].iloc[i])])
                apneas.append(apnea)
            i+=1
    if len(apneas) < 1:
        sigh.lack() #if there are no apneas after the sigh, the sigh may be a sniff, and needs to be highlighted differently
    return apneas

def matching_apnea(start_time,apneas):
    return any(
        apnea.start_time == start_time #if there's another apnea that has the same start time as the input, return True
        for apnea in apneas
    )

def type3_apnea(peak_data, apneas):
    i = 0
    while i < len(peak_data) - 2:
        if peak_data["Start"].iloc[i+1] - (peak_data["Start"].iloc[i]+ peak_data["Width"].iloc[i]) > 0.7999 and (not matching_apnea(peak_data["Start"].iloc[i]+ peak_data["Width"].iloc[i],apneas)): 
             #if there's a gap in the peaks big enough for an apnea AND it's not an apnea already saved, it's a type 3
             apnea = Apnea("3", peak_data["Start"].iloc[i]+peak_data["Width"][i], [peak_data["Start"].iloc[i+1] - (peak_data["Start"][i] + peak_data["Width"][i])])
             apneas.append(apnea)
        i+=1
    return apneas

def apnea_combination(normalized_signal, apneas): #no idea if I wrote this correctly yet
    removed_apneas = []
    for apnea in apneas:
        extended_view = peak_analysis(normalized_signal, apnea.start_time)
        ev_hmean, ev_amean = peak_means(extended_view)
        sigh_caught = find_sighs(extended_view,ev_hmean,ev_amean)
       
        if len(sigh_caught) > 0:
            apnea.duration.append(apnea2.duration[0] for apnea2 in apneas if apnea.start_time < apnea2.start_time < sigh_caught[0].start_time)
            removed_apneas.append(apnea2 for apnea2 in apneas if apnea.start_time < apnea2.start_time < sigh_caught[0].start_time )
        else:
            apnea.duration.append(apnea2.duration[0] for apnea2 in apneas if apnea.start_time < apnea2.duration[0] < extended_view["Time"].iloc[0])
            removed_apneas.append(apnea2 for apnea2 in apneas if apnea.start_time < apnea2.start_time < extended_view["Time"].iloc[0])

    apneas = [apnea for apnea in apneas if apnea not in removed_apneas]
    return apneas
