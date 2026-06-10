import numpy as np
import scipy
import matplotlib as plt
import cv2
import pandas as pd
import xlrd
#im probably going to need to narrow these libraries when I get the chance
#I think apneas can be saved as dicts
    #apnea = {"start time": x, "duration": [y]}

pleth_graph_excel = input()
pleth_graph = pd.read_excel(pleth_graph_excel)

#Parse 20 seconds
#take the first half
#Yawn check
    #yawn confirmed? apnea check
    #write the apnea down
#Apnea check (0.8 second duration etc)
    #apnea found: already exists?
        #if so, ignore
        #if not, write that down

#Run through apneas
    #another one within 10 seconds AND no yawn in between?
        #list durations but combine start time
            #^ ok but that needs to be saved through another method so the highlighting is accurate

#Save the 10 second list of apneas to an excel sheet and run through the chunk again


