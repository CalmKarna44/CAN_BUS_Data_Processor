import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from datetime import datetime

df = pd.read_csv(r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\TS Reading Practice 2.csv")

df.columns = df.columns.str.strip() # Strip of white spaces at beginning and end of column names

print (df.columns.tolist()) # Printing cleaned column names to be used in the melt statement as the value for variables.  

df_long = df.melt(id_vars="Lap Number",var_name="Drivers", value_vars=['Lap Number', 'Kirk Barron', 'Tom', 'fattfill', 'Michael Currer', 'Dusten', 'Shivam Patel', 'Chaitanya Sakre', 'ahmed husien', 'IARA AFONSO'], value_name= "Lap Times")


def time_to_seconds(t):
    if pd.isna(t):
        return np.nan
    
    if isinstance(t,str) and ":" in t:
        laps_clean = datetime.strptime(t,"%M:%S.%f")
        return laps_clean.minute * 60 + laps_clean.second + laps_clean.microsecond/1e6
    
    return float(t)

df_long["Lap Times"] = df_long["Lap Times"].apply(time_to_seconds)

df_clean = df_long.dropna()

df_fast = df_clean[df_clean["Lap Times"] <= 40]

fastest = df_fast.groupby("Drivers")["Lap Times"].min()
print(fastest)
average = round (df_fast.groupby("Drivers")["Lap Times"].mean(),3)
print (average)
consistency = round(df_fast.groupby("Drivers")["Lap Times"].std(),3)
print(consistency)

idx = df_fast["Lap Times"].idxmin()
fastest_lap_overall = df_fast.loc[idx]
print(fastest_lap_overall)