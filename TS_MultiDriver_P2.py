import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from datetime import datetime

df = pd.read_csv(r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\TS Reading Practice 2.csv")

df.columns = df.columns.str.strip() # Strip of white spaces at beginning and end of column names

print (df.columns.tolist()) # Printing cleaned column names to be used in the melt statement as the value for variables.  

#melting the wide form table into long form table
df_long = df.melt(id_vars="Lap Number",var_name="Drivers", value_vars=['Lap Number', 'Kirk Barron', 'Tom', 'fattfill', 'Michael Currer', 'Dusten', 'Shivam Patel', 'Chaitanya Sakre', 'ahmed husien', 'IARA AFONSO'], value_name= "Lap Times")

#Clean lap times (we had numbers input in the minute,second and millisecs form so no need of string converstion)
#So we are converting minutes into seconds here. 
def time_to_seconds(t):
    if pd.isna(t):
        return np.nan
    
    if isinstance(t,str) and ":" in t:
        laps_clean = datetime.strptime(t,"%M:%S.%f")
        return laps_clean.minute * 60 + laps_clean.second + laps_clean.microsecond/1e6
    
    return float(t)

df_long["Lap Times"] = df_long["Lap Times"].apply(time_to_seconds)

df_clean = df_long.dropna() # Remove NAN values from the dataframe 

#Filtering out fast laps 
df_fast = df_clean[df_clean["Lap Times"] <= 40]

#Printing values
fastest = df_fast.groupby("Drivers")["Lap Times"].min()
print(fastest)
average = round (df_fast.groupby("Drivers")["Lap Times"].mean(),3)
print (average)
consistency = round(df_fast.groupby("Drivers")["Lap Times"].std(),3)
print(consistency)

idx = df_fast["Lap Times"].idxmin()
fastest_lap_overall = df_fast.loc[idx]
print(fastest_lap_overall)

#Created a dictionary of the laps of each driver to be printed or accessed easily
driver_laps_dict = {}
for driver, data in df_clean.groupby("Drivers"):
    driver_laps_dict[driver] = data.sort_values("Lap Number")

print(driver_laps_dict["fattfill"])

#Color Coding the drivers
class PlotStyle: 
    def __init__(self, driver):
        colors = plt.cm.tab10.colors
        self.driver_colors = {
            driver: colors[x % len(colors)]
            for x, driver in enumerate(driver)
        }

style = PlotStyle(df_clean["Drivers"].unique())

#Plotting the fast laps with average pace of each driver. 
plt.figure(figsize=(12,7))

for driver,data in df_fast.groupby("Drivers"):
    color = style.driver_colors[driver]
    avg = round (data["Lap Times"].mean(),3)
    plt.plot(data["Lap Number"], data["Lap Times"],marker="o", label= driver, color = color)  
    plt.axhline(avg, linestyle = "--", linewidth = 1.5,color = color, label = f"Avg Pace: {avg} s")

plt.xlabel("Lap Number")
plt.ylabel("Lap Times (s)")
plt.title("Lap Time trend per Driver")
plt.legend(loc = "upper right", bbox_to_anchor = (1.22,1), borderaxespad = 0, ncol=1) #Learned plotting legend outside the graph
plt.xticks(df_fast["Lap Number"])
plt.grid(True)
plt.tight_layout()

#Plotting the rolling average of the drivers
plt.figure(figsize=(10, 6))

for driver, data in df_fast.groupby("Drivers"):
    data = data.sort_values("Lap Number")
    color = style.driver_colors[driver]
    rolling_mean = data["Lap Times"].rolling(window=3).mean()
    
    if not rolling_mean.notna().any():
        continue
    
    plt.plot(
        data["Lap Number"],
        rolling_mean,
        linewidth=2,
        color= color, 
        label=f"{driver} (3-lap avg)"
    )

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (s)")
plt.title("Rolling Average Pace")
plt.legend(loc = "upper left", bbox_to_anchor = (1.02,1), borderaxespad = 0, ncol=1)
plt.grid(True)
plt.xticks(df_fast["Lap Number"])
plt.tight_layout()
plt.show()