from scipy import signal as scp
from scipy.integrate import trapezoid
import matplotlib.pyplot as plt
import pandas as pd


class Apnea:
    def __init__(self,type,start_time,end_time):
        self.duration = start_time - end_time #need to update to fit list type 
        self.start_time = start_time
        self.type = type
    def print(self):
        print(f"Duration: {self.duration}, Start: {self.start_time}, Type: {self.type}")
    
class Sigh:
    def __init__(self,start_time,end_time):
        self.duration = start_time - end_time
        self.start_time = start_time
    def print(self): #defining because it's useful for checking things
        print(f"Duration: {self.duration}, Start: {self.start_time}")


#im probably going to need to narrow these libraries when I get the chance
#I think apneas can be saved as dicts
    #apnea = {"start time": x, "duration": [y]}

chunk_value = 20
sampling_interval = 2000
Nrows = chunk_value * sampling_interval #total number of rows
skip_rows = sampling_interval * 3600 #THIS skips the first hour
print("Paste the file location of the pleth ASCII (no headings, no quotation marks)")
pleth_location = input()
pleth_graph_ascii = pleth_location
#dtype = np.float64
    #this may change based on how time is listed in the excel file
    #actually i can just ignore that column if need be, or use parse date-time
#specify columns based on how the final data generates
#check the .xls type to determine engine
#nrows = sampling interval per second * 20
pleth_section = pd.read_csv(pleth_graph_ascii, sep="\\s+",index_col=False, skiprows=skip_rows, nrows=Nrows, low_memory=False, header=0, names=["Time","Flow"]) 
print(pleth_section)
    #returns a dataframe
#pleth_section.plot(x="Time",y="Flow")
#plt.show()
#shows the plot of flow

#define the baseline 
base_flow = -16.4 #probably won't need this after normalization lmao
#normalize the signal (probably z-score)
normalized_ps = pleth_section.copy()
normalized_ps["Flow"] = (pleth_section["Flow"]-pleth_section["Flow"].mean())/pleth_section["Flow"].std()
#print(normalized_ps)

#take the first half
pleth_ten_section = normalized_ps.head(len(normalized_ps) // 2).copy() 
pleth_ten_section.plot(x="Time",y="Flow")
print(pleth_ten_section)
#plt.show()

#I don't think I need the gradient anymore, but, if it's needed later use np.gradient


#Collect the local maximums of a certain height within the first 10 seconds
pts_peaks_tp = scp.find_peaks(pleth_ten_section["Flow"], height=1.1*pleth_ten_section['Flow'].std())
pts_peaks_loc = pts_peaks_tp[0]*0.0005 + 3600
pts_peaks_w =scp.peak_widths(pleth_ten_section["Flow"], pts_peaks_tp[0])
print(pts_peaks_w)
pts_peaks_height = pts_peaks_tp[1]["peak_heights"]
pts_peaks_width = pts_peaks_w[0]*0.0005
#plt.plot(pts_peaks_loc,pts_peaks_height,"x")

    #probably can check all data above N std deviation above the mean and take the peaks with the gradient graph
    #so take the maxs using the gradient, if that point on the regular graph meets the minimum height requirement, sae it
    #noting the start and end of those maximums too 

#take the area under the maximums using their starts and ends
    #save that data too

#take the average of the maximum heights and average of maximum areas

#Sigh check:
sighs = pd.DataFrame(columns=['Time','Height','Width'])
ptsp_data = {'Time': pts_peaks_loc, 'Height': pts_peaks_height, 'Width': pts_peaks_width}
ptsp_dataframe = pd.DataFrame(data=ptsp_data)


ptsp_dataframe=ptsp_dataframe.sort_values(by='Height',ascending=False)
ptsp_mean = ptsp_dataframe['Height'].mean()
ptsp_area_mean = ptsp_dataframe['Width'].mean()

for index, row in ptsp_dataframe.iterrows(): #going through all the peaks
    if row['Height'] > 1.25*ptsp_mean: #basis definition for a sigh
        if row['Width'] > 2.25*ptsp_area_mean: #other definition for a sigh
            sighs.concat(row) #I'm going to fix this to fit the sigh object soon

#using lpf to see if we can isolate apneas, they tend to be high frequency
lpf = scp.butter(1, 6, fs=2000, output='sos')
pts_filtered = scp.sosfilt(lpf, pleth_ten_section['Flow'])
plt.plot(pleth_ten_section['Time'], pts_filtered)
plt.axhspan(-2*pleth_ten_section['Flow'].std(), 0.3*pleth_ten_section['Flow'].std(), color='lightgreen', alpha=0.3)
plt.show()

#Got sighs? apnea check
if len(sighs) >= 1:
    for index, sigh in sighs:
        #something, something, checking for apneas
        #note the sigh then expand 10 seconds out from the sigh
        #breaths within a certain std dev after that sigh? that period last at or more than 0.8 seconds? call it type 2
        #apnea pattern appears not directly after the sigh? call it type 1
            #differentiating between type 1 & 2 does not matter as much rn 
        break
else: #no sighs? look for type 3s 
    x = 2
    #^ my "go away error" methodology
        #looking for sections within a certain range that last > 0.8 seconds
        #if there's an apnea, call it, and label it type 3

    
#Run through apneas
    #another one within 10 seconds AND no sigh in between?
        #list durations but combine start time
            #^ ok but that needs to be saved through another method so the highlighting is accurate

#Save the 10 second list of apneas to a dataframe or excel sheet and run through the next 10 second section via 20 second chunk


