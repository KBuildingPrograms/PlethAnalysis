import tkinter as tk
from tkinter.filedialog import askopenfilename
import polars as pl
import pandas as pd
import tqdm

window = tk.Tk()

def switch_data():
   csv_path = askopenfilename()
   csv_path = csv_path.replace("\"","")
   print("Loading")
   csv_data = pd.read_csv(csv_path,sep="\\s+",index_col=False,names=["Time","Flow"],header=27,chunksize=100000,dtype={"Time":"float32","Flow":"float32"})

   print("Generating Path")
   parquet_path = csv_path.replace(".ascii",".parquet")
   print("Moving to parquet")
   final_dataframe = pl.DataFrame(schema={"Time":pl.Float32,"Flow":pl.Float32})
   for chunk in tqdm.tqdm(csv_data):
      final_dataframe.extend(pl.from_pandas(chunk))
   print(final_dataframe)
   final_dataframe.write_parquet(parquet_path,compression="zstd",compression_level=3,statistics=False)
   print("Done!")

ascii_button = tk.Button(window,text='Grab Ascii',command=switch_data)
ascii_button.pack()
window.mainloop()