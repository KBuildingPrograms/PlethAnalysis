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

#im probably going to need to narrow these libraries when I get the chance
#I think apneas can be saved as dicts
    #apnea = {"start time": x, "duration": [y]}

chunk_value = 20
sampling_interval = 2000
Nrows = chunk_value * sampling_interval #total number of rows
skip_rows = sampling_interval * 3600 #THIS skips the first hour, this has to update in the final version
print("Paste the file location of the pleth ASCII (no headings)")
pleth_location = input()
pleth_graph_ascii = pleth_location[1:len(pleth_location)-1]
#dtype = np.float64
    #this may change based on how time is listed in the excel file
    #actually i can just ignore that column if need be, or use parse date-time
#specify columns based on how the final data generates
#check the .xls type to determine engine
#nrows = sampling interval per second * 20
pleth_section = pd.read_csv(pleth_graph_ascii, sep="\\s+",index_col=False, skiprows=skip_rows, nrows=Nrows, low_memory=False, header=0, names=["Time","Flow"]) 
    #returns a dataframe
#pleth_section.plot(x="Time",y="Flow")
#plt.show()
#shows the plot of flow

#define the baseline 
#normalize the signal (probably z-score)
normalized_ps = pleth_section.copy()
normalized_ps["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()
#print(normalized_ps)

#take the first half
pleth_ten_section = normalized_ps.head(len(normalized_ps) // 2).copy() 
pleth_ten_section.plot(x="Time",y="Flow")


#I don't think I need the gradient anymore, but, if it's needed later use np.gradient


#Collect the local maximums of a certain height within the first 10 seconds
pts_peaks_tp = scp.find_peaks(pleth_ten_section["Flow"], height=1.1*pleth_ten_section['Flow'].std())
pts_peaks_loc = pts_peaks_tp[0]*0.0005 + 3600
pts_peaks_w =scp.peak_widths(pleth_ten_section["Flow"], pts_peaks_tp[0],rel_height=0.6)
pts_peaks_height = pts_peaks_tp[1]["peak_heights"]
pts_peaks_width = pts_peaks_w[0]*0.0005 
pts_peaks_start = pts_peaks_w[2]*0.0005 + 3600
plt.hlines(pts_peaks_w[1],pts_peaks_start, pts_peaks_width+pts_peaks_start,color="C3")

 

#Sigh check:
sighs = []
apneas = []
new_sigh = None
ptsp_data = {'Time': pts_peaks_loc, 'Height': pts_peaks_height, 'Width': pts_peaks_width, 'Start': pts_peaks_start}
ptsp_dataframe = pd.DataFrame(data=ptsp_data)


ptsp_dataframe=ptsp_dataframe.sort_values(by='Height',ascending=False)
ptsp_mean = ptsp_dataframe['Height'].mean()
ptsp_area_mean = ptsp_dataframe['Width'].mean() * ptsp_dataframe['Height'].mean()

for index, row in ptsp_dataframe.iterrows(): #going through all the peaks
    if row['Height'] > 1.25*ptsp_mean: #basis definition for a sigh
        if row['Width'] > 0.7*ptsp_area_mean: #other definition for a sigh
            new_sigh = Sigh(row['Start'],row['Width'])
            print(new_sigh)
            sighs.append(new_sigh)
            


plt.axhspan(-2*pleth_ten_section['Flow'].std(), 0.3*pleth_ten_section['Flow'].std(), color='lightgreen', alpha=0.3)
try:
    plt.axvspan(getattr(new_sigh, "start_time"), getattr(new_sigh, "start_time") + getattr(new_sigh, "duration"), color='blue', alpha=0.3 )
except:
    pass
#plt.show()

#Got sighs? apnea check
if len(sighs) >= 1:
    plt.axhspan(-2*pleth_ten_section['Flow'].std(), 0.4*pleth_ten_section['Flow'].std(), color='lightgreen', alpha=0.3)
    plt.show()
    for sigh in sighs:
        extended_view = normalized_ps.loc[(sigh.start_time > normalized_ps['Time']) & (normalized_ps['Time'] < sigh.start_time + 10), ['Time','Flow']] #extending 10 seconds out from sigh
        extended_peaks_tp = scp.find_peaks(extended_view["Flow"], height=1.2*extended_view['Flow'].std())
        extended_peaks_w = scp.peak_widths(extended_view['Flow'], extended_peaks_tp[0],rel_height=0.6)
        extended_peaks_width = extended_peaks_w[0]*0.0005
        extended_peaks_start = extended_peaks_w[2]*0.0005 + extended_view['Time'].iloc[0]
        i=0
        while  i < len(extended_peaks_width)-1: #this...is probably not the right way to write this, but you get the gist 6/18
            if extended_peaks_start[i+1] - (extended_peaks_start[i] + extended_peaks_width[i]) > 0.8: #eventually want to change 0.8 to 0.7999
                apnea = Apnea("1/2",extended_peaks_start[i] + extended_peaks_width[i], [extended_peaks_start[i+1] - (extended_peaks_start[i] + extended_peaks_width[i])])
                apneas.append(apnea)
            i+=1
        if len(apneas) < 1:
            sigh.lack()
       #Still need to differentiate between type 1 and 2
else: #no sighs? look for type 3s 
    i = 0
    while i < len(pts_peaks_width)-1:
        if pts_peaks_start[i+1] - (pts_peaks_start[i] + pts_peaks_width[i]) > 0.8:
            apnea = Apnea("3", pts_peaks_start[i]+pts_peaks_width[i], pts_peaks_start[i+1], pts_peaks_start[i+1] - (pts_peaks_start[i] + pts_peaks_width[i]))
    i+=1


    
#Run through apneas
if len(apneas) > 0:
    for apnea in apneas:
        extended_view = normalized_ps.loc[(apnea.start_time < normalized_ps['Time']) & (normalized_ps['Time'] < apnea.start_time + 10), ['Time','Flow']] #extending 10 seconds out from apnea
        extended_peaks_tp = scp.find_peaks(extended_view["Flow"], height=1.2*extended_view['Flow'].std())
        extended_peaks_w = scp.peak_widths(extended_view['Flow'], extended_peaks_tp[0],rel_height=0.6)
        extended_peaks_width = extended_peaks_w[0]*0.0005
        extended_peaks_start = extended_peaks_w[2]*0.0005 + extended_view['Time'].iloc[0]
        extended_view.plot(x="Time",y="Flow")
        plt.hlines(extended_peaks_w[1],extended_peaks_start, extended_peaks_width+extended_peaks_start,color="C2")
        plt.show()
    #another one within 10 seconds AND no sigh in between?
        i=0
        while  i < len(extended_peaks_width)-1: #this...is probably not the right way to write this, but you get the gist 6/18
            if extended_peaks_start[i+1] - (extended_peaks_start[i] + extended_peaks_width[i]) > 0.8: #eventually want to change 0.8 to 0.7999
                #I think I need to add sigh detection in the final, more organized version of everything
                apnea.duration.append(extended_peaks_start[i+1] - (extended_peaks_start[i] + extended_peaks_width[i]))
            i+=1
        #list durations but combine start time
            #^ ok but that needs to be saved through another method so the highlighting is accurate

#Save the 10 second list of apneas to a dataframe or excel sheet and run through the next 10 second section via 20 second chunk


