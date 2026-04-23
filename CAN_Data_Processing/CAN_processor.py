from asammdf import MDF 
import cantools 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import tkinter as tk 
from tkinter import filedialog
import os 

def load_dbc(dbc_path):
    db = cantools.database.load_file(dbc_path)
    print (f"DBC loaded : {dbc_path}")
    print (f"Messages : {len(db.messages)}")
    return db 

def load_mf4(mf4_path): 
    mdf = MDF(mf4_path)
    raw_df = mdf.to_dataframe()
    rename_map = {}
    for col in raw_df.columns:
        short_name = col.split('.')[-1]
        rename_map[col] = short_name
        
    raw_df = raw_df.rename(columns=rename_map)

    print (f"MF4 loaded : {mf4_path}")
    print(f"Total frames  : {len(raw_df)}")
    print(f"Time range    : {raw_df.index[0]}s → {raw_df.index[-1]}s")

    return raw_df

def filter_obd2(raw_df, can_id = 0x7E8):
    obd2_df = raw_df[raw_df["ID"]==can_id].copy()
    print (f"OBD2 Frames : {len(obd2_df)}  (ID= {can_id})")

    return obd2_df

def decode_obd2(obd2_df, db, can_id = 0x7E8):
    decoded_records = []
    for timestamp, row in obd2_df.iterrows():
        raw_bytes = bytes(row["DataBytes"])

        try: 
            decoded = db.decode_message(can_id, data = raw_bytes, decode_choices = False)
            decoded["timestamps"] = timestamp
            decoded_records.append(decoded)

        except Exception as e: 
            print(f"Could not decode frame at {timestamp:.4f}s : {e}")
            pass

    decoded_df = pd.DataFrame(decoded_records)
    decoded_df = decoded_df.set_index("timestamps")

    real_signals = []
    for message in db.messages:
        for sig in message.signals:
            if sig.unit is not None: 
                real_signals.append(sig.name)

    signals_found = []
    for col in decoded_df.columns:
        if col in real_signals:
            signals_found.append(col)

    print(f"Real signals found : {signals_found}")        
    print (f"Decoded Signals : {len(decoded_df)}")

    return decoded_df, signals_found

def signal_stats(decoded_df, signal_found):
    stats_store = {}
    for signals in signal_found:
        stats = decoded_df[signals].dropna().describe()
        stats_store[signals] = stats

    for sig_name, stats in stats_store.items():
        print (f"--- {sig_name} ---")
        print (f" Samples             : {int(stats["count"])}")
        print (f" Min Value           : {stats["min"]:.2f}")
        print (f" Max Value           : {stats["max"]:.2f}")
        print (f" Mean Value          : {stats["mean"]:.2f}")
        print (f" Median Value        : {stats["50%"]:.2f}")
        print (f" Std deviation Value : {stats["std"]:.2f}")
        print ()

    return stats_store

def plot_signals(decoded_df, signals, title='OBD2 Data'):

    colours = [
        'red', 'blue', 'green', 'indigo',
        'orange', 'purple', 'brown', 'pink', 'magenta', 'olive', 'darkgreen', 'darkblue'
    ]

    fig = make_subplots(
        rows             = len(signals),
        cols             = 1,
        shared_xaxes     = False,
        subplot_titles   = signals,
        vertical_spacing = 0.05
    )

    for i, sig_name in enumerate(signals):
        sig_data = decoded_df[sig_name].dropna()
        colour   = colours[i % len(colours)]  # cycles through colours

        fig.add_trace(
            go.Scatter(
                x    = sig_data.index,
                y    = sig_data.values,
                mode = 'lines',
                name = sig_name,
                line = dict(color=colour, width=1)
            ),
            row = i + 1,
            col = 1
        )

    fig.update_layout(
        title         = title,
        height        = 250 * len(signals),
        width         = 500 * len(signals),
        plot_bgcolor  = 'white',
        paper_bgcolor = 'white'
    )

    fig.update_xaxes(
        showgrid  = True,
        gridcolor = 'black',
        gridwidth = 0.5, 
        layer     = 'below traces',
        title_text='Time (seconds)', 
        row=len(signals), 
        col=1
    )
    fig.update_yaxes(
        showgrid  = True,
        gridcolor = 'black',
        gridwidth = 0.5,
        layer     = 'below traces',

    )
    fig.show()
        
def file_save(decoded_df, signals_found):
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title = "Select folder to save the csv.")
    print (f"Selected folder: {folder_path}")

    if not folder_path: 
        print("Save cancelled - No folder selected.")
        return 

    file_name = input("Please input file name without .csv: ")
    print(f"File name will be saved as {file_name}.csv")

    if not file_name.strip():
        print ("Save cancelled - No file name given")
        return

    file_path = os.path.join (folder_path, f"{file_name}.csv")
    
    decoded_df[signals_found].to_csv(file_path)
    print(f"Saved to : {file_path}")
    print (f"Number of rows: {len(decoded_df)}")
    print (f"Columns : {list(decoded_df.columns)}")