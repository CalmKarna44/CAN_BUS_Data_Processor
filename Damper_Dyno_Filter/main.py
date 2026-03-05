import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt


csv_import_file = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\Charlie New Damper Data\FL_10_clicks.csv"

alpha = 0.5 
epsilon = 2.0 

df = pd.read_csv(csv_import_file)

# FIND VELOCITY + FORCE COLUMNS

cols_lower = []
for c in df.columns:
    cols_lower.append(c.lower().strip())
    
print (cols_lower)
vel_column = None
force_column = None

for i, c in enumerate(cols_lower): 
    if "velocity" in c or c.startswith("vel"):
        vel_column = df.columns[i]

    if "force" in c or "load" in c: 
        force_column = df.columns[i]
    
# Manual Column Selection 
if vel_column is None or force_column is None: 
    print ("Could not find Velocity or Force Column automatically")
    print ("The available columns in the data are: ")
    for i, c in enumerate(df.columns):
        print (f"{i}:{c}")

    if vel_column is None: 
        while True: 
            try:
                vel_idx = int(input("Enter the column index for Velocity: "))
                vel_column = df.columns[vel_idx]
                print(f"The velocity column is : {vel_column}")
                break 
            except (ValueError, IndexError):
                print ("Invalid Input! Please enter correct index of Velocity column")

    if force_column is None: 
        while True: 
            try:
                force_idx = int(input("Enter the column index for Force: "))
                force_column = df.columns[force_idx]
                print (f"The force column is : {force_column}")
                break
            except (ValueError, IndexError):
                print ("Invalid Input! Please enter correct index of Velocity column")


print(f"Using Velocity Column: {vel_column} as Velocity")
print(f"Using Force Column: {force_column} as Force" )

new_df = df[[vel_column,force_column]].copy()
new_df.columns = ["Velocity", "Force"]

#Converting it to numeric 
new_df["Velocity"] = pd.to_numeric(new_df["Velocity"], errors = "raise")
new_df ["Force"] = pd.to_numeric(new_df["Force"], errors= "raise")

#Drop completely invalid rows (NAN, NAN)
new_df = new_df.dropna(subset = ["Velocity", "Force"], how = "all").reset_index(drop=True)

# Dead Band Removal 
new_df = new_df[new_df["Velocity"].abs() > epsilon].reset_index(drop = True)

#EWMA Filter
new_df["Force_Filtered"] = np.nan

new_df.loc[0, "Force_Filtered"] = new_df.loc [0, "Force"]

for i in range(1, len(new_df)): 
    v_current = new_df.loc[i, "Velocity"]
    v_previous = new_df.loc[i-1, "Velocity"]

    F_current = new_df.loc[i, "Force"]
    F_prev_filtered = new_df.loc[i-1, "Force_Filtered"]

    if v_current * v_previous < 0: 
        new_df.loc[i, "Force_Filtered"] = new_df.loc [i, "Force"]
    else:
        new_df.loc[i, "Force_Filtered"] = alpha*F_current + (1-alpha)*F_prev_filtered

new_df["Force_Filtered"] = new_df["Force_Filtered"].round(3)
print (new_df)

bump_df = new_df[new_df["Velocity"]>0].copy()
rebound_df = new_df[new_df["Velocity"]<0].copy()

#Sanity Check 
print("Number of NAN values: ", new_df["Force_Filtered"].isna().sum()) 
print ("Bump Rows: ", len(bump_df))
print ("Rebound Rows: ", len(rebound_df))

print("Bump velocity min/max:", bump_df["Velocity"].min(), bump_df["Velocity"].max())
print("Rebound velocity min/max:", rebound_df["Velocity"].min(), rebound_df["Velocity"].max())

# Plotting 
plt.figure()
plt.plot(df[vel_column], df[force_column], color = "red", label = "Original Data")
plt.plot(new_df["Velocity"], new_df["Force_Filtered"], color = "green", label = "Filtered Data")

plt.xlabel ("Velocity (mm/sec)")
plt.ylabel ("Force (N)")
plt.title ("Comparison for validation")
plt.legend()
plt.grid(True)
plt.show()


