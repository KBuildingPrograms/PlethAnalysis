import polars as pl
import pandas as pd

csv_path = input("Paste path of ASCII here:")
csv_path = csv_path.replace("\"","")
print("Loading")
csv_data = pd.read_csv(csv_path,sep="\\s+",index_col=False,names=["Time","Flow"],header=0,chunksize=100000)

print("Generating Path")
parquet_path = csv_path.replace(".ascii",".parquet")
print("Moving to parquet")
for chunk in csv_data:
    polar_chunk = pl.from_pandas(chunk)
    polar_chunk.write_parquet(parquet_path)
print("Done!")