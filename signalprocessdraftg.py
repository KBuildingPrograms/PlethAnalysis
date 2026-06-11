import numpy as np
from sklearn import svm
from scipy.integrate import trapz
import matplotlib as plt
import pandas as pd


class Apnea:
    def __init__(self,type,start_time,end_time):
        self.duration = start_time - end_time
        self.start_time = start_time
        self.type = type
    
class Yawn:
    def __init__(self,start_time,end_time):
        self.duration = start_time - end_time
        self.start_time = start_time


#im probably going to need to narrow these libraries when I get the chance
#I think apneas can be saved as dicts
    #apnea = {"start time": x, "duration": [y]}

chunk_value = 20
sampling_interval = 2000
Nrows = chunk_value * sampling_interval + (sampling_interval * 3600) #skip the first hour
pleth_graph_ascii = input()
#dtype = np.float64
    #this may change based on how time is listed in the excel file
    #actually i can just ignore that column if need be, or use parse date-time
#specify columns based on how the final data generates
#check the .xls type to determine engine
#nrows = sampling interval per second * 20
pleth_section = pd.read_csv(pleth_graph_ascii, sep="\s+",) 
print(pleth_section)
    #returns a dataframe


#take the first half
pleth_ten_section = pleth_section.sample(frac=0.5)

#define the baseline 
#normalize the signal (probably z-score)
    #plot the section using the dataframe plot or matplotlib
#take the derivative of the data
    #either df.pct_change() or np.gradient()
    #plot the gradient to check it


#Collect the local maximums of a certain height within the first 10 seconds
    #probably can check all data above N std deviation above the mean and take the peaks with the gradient graph
    #so take the maxs using the gradient, if that point on the regular graph meets the minimum height requirement, sae it
    #noting the start and end of those maximums too 

#take the area under the maximums using their starts and ends
    #save that data too

#take the average of the maximum heights and average of maximum areas

#Yawn check: 
    #find a minimum that is ~25% taller than the average minimum
        #check if its area is 120%+ greater than the average area
            #if so, yawn confirmed! add it to the yawn counter

#Apnea checks are where I think I'd like to use SVM the most
#Got yawns? apnea check
    #note the yawn then expand 10 seconds out from the yawn
    #breaths within a certain std dev after that yawn? that period last at or more than 0.8 seconds? call it type 2
    #apnea pattern appears not directly after the yawn? call it type 1

#No yawns? type 3 check
    #same type of apnea check in terms of looking for *very small breaths* over 0.8 seconds
    #if there's an apnea, call it, and label it type 3

#Run through apneas
    #another one within 10 seconds AND no yawn in between?
        #list durations but combine start time
            #^ ok but that needs to be saved through another method so the highlighting is accurate

#Save the 10 second list of apneas to a dataframe or excel sheet and run through the next 10 second section via 20 second chunk


