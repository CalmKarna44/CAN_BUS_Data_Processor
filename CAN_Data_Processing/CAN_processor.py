from asammdf import MDF 
import cantools 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import tkinter as tk 
from tkinter import filedialog
import os 
import logging

logging.basicConfig(
    filename="CAN_processor_logfile.log",
    filemode = "a", 
    level= logging.DEBUG, 
    format = "%(asctime)s | %(levelname)s | %(message)s", 
    datefmt=  " %d-%m-%Y %H:%M:%S "
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

def load_dbc(dbc_path):                                       
    
    # Explaination: Load the proprietary database to return cantools database for decoding all CAN Signals
    try:
        db = cantools.database.load_file(dbc_path, strict = False)
        logging.info(f"Propritery DBC loaded : {dbc_path}")
        logging.info(f"Propritery DBC Messages : {len(db.messages)}")
        return db
    
    except Exception as e: 
        logging.error (f"Failed to load DBC: {dbc_path} : {e}")
        return None 

def load_obd2_dbc(obd2_dbc_path):    

    # Explaination: Similar to above but now loading the OBD2 database for decoding OBD2 signals

    obd2_db = cantools.database.load_file(obd2_dbc_path)
    print (f"OBD2 DBC loaded : {obd2_dbc_path}")
    print (f"OBD2 DBC Messages : {len(obd2_db.messages)}")

    return obd2_db

def select_file():  

    # Explaination: Open a GUI file picker for MF4 file selection. It returns selected file path or None if cancelled. 

    root = tk.Tk()
    root.withdraw()

    open_file_path = filedialog.askopenfilename(
        title="Select MF4 File",
        filetypes=[("MF4 files", "*.MF4")]
    )

    if not open_file_path: 
        print("No file selected.")
        return 
    
    print (f"Selected file : {open_file_path}")
    return open_file_path

def load_mf4(mf4_path): 

    # Explaintion: Load an MF4 file and return a normalised raw CAN DataFrame. Column names are shortened by removing asammdf prefixes.
    try: 
        mdf = MDF(mf4_path)
        raw_df = mdf.to_dataframe()
        rename_map = {}
        for col in raw_df.columns:
            short_name = col.split('.')[-1]
            rename_map[col] = short_name
        raw_df = raw_df.rename(columns=rename_map)

        logging.info (f"MF4 loaded : {mf4_path}")
        logging.info (f"Total frames  : {len(raw_df)}")
        logging.info (f"Time range    : {raw_df.index[0]}s → {raw_df.index[-1]}s")

        return raw_df

    except Exception as e: 
        logging.error(f"Failed to load MF4 file: {mf4_path} : {e}")
        return None

def decode_raw_can(raw_df, db):

    # Explaination:  Decode raw CAN frames directly against a proprietary DBC. Each frame ID maps directly to a message in the DBC.

    dbc_ids = {int(message.frame_id): message for message in db.messages}

    decoded_records = []
    skipped = 0 

    for timestamp, row in raw_df.iterrows():
        frame_id = int(row["ID"])
        raw_bytes = bytes(row["DataBytes"])

        if frame_id not in dbc_ids:
            skipped += 1
            continue

        try:
            decoded = db.decode_message(frame_id, raw_bytes, decode_choices = False)
            decoded["timestamp"] = timestamp
            decoded["message"] = dbc_ids[frame_id].name
            decoded_records.append(decoded)

        except Exception as e:
            skipped += 1
            logging.debug(f"Failed to decode frame {frame_id} : {e}")
    
    if not decoded_records:
        print("No frames were decoded — check DBC matches MF4")
        return None, []

    decoded_df = pd.DataFrame(decoded_records)
    decoded_df = decoded_df.set_index("timestamp")

    print (f"Total Frames : {len(raw_df)}")
    print (f"Decoded Frames : {len(decoded_records)}")
    print (f"Skipped Frames : {skipped}")
    print (f"Signals Found : {list(decoded_df.columns)}")

    signals_found = list(decoded_df.columns)

    return decoded_df, signals_found


def filter_obd2(raw_df, can_id = 0x7E8):

    # Explaination: Filter raw CAN DataFrame to only OBD2 response frames.

    obd2_df = raw_df[raw_df["ID"]==can_id].copy()
    print (f"OBD2 Frames : {len(obd2_df)}  (ID= {can_id})")

    if obd2_df.empty:
        print ("No OBD2 frames found in the selected MF4 file")
        return None

    return obd2_df

def decode_obd2(obd2_df, obd2_db, can_id = 0x7E8):
    
    """
    Explaination: Decode raw OBD2 frames into physical signal values. 
    Automatically filters to real signals using DBC unit definitions.
    """

    decoded_obd2_records = []
    for timestamp, row in obd2_df.iterrows():
        raw_bytes = bytes(row["DataBytes"])

        try: 
            decoded_obd2 = obd2_db.decode_message(can_id, data = raw_bytes, decode_choices = False)
            decoded_obd2["timestamps"] = timestamp
            decoded_obd2_records.append(decoded_obd2)

        except Exception as e: 
            logging.debug(f"Could not decode frame at {timestamp:.4f}s : {e}")
            pass

    decoded_obd2_df = pd.DataFrame(decoded_obd2_records)
    decoded_obd2_df = decoded_obd2_df.set_index("timestamps")

    real_obd2_signals = []
    for message in obd2_db.messages:
        for sig in message.signals:
            if sig.unit is not None:                   # Only keeping signals with meaningful units
                real_obd2_signals.append(sig.name)

    obd2_signals_found = []
    for col in decoded_obd2_df.columns:
        if col in real_obd2_signals:
            obd2_signals_found.append(col)

    print(f"Real signals found : {obd2_signals_found}")        
    print (f"Decoded Signals : {len(decoded_obd2_df)}")

    return decoded_obd2_df, obd2_signals_found

def signal_stats(decoded_obd2_df, obd2_signals_found):

    # Explaination: Calculate and print descriptive statistics for each signal.Skips non-numeric columns automatically.

    stats_store = {}
    for signals in obd2_signals_found:
        stats = decoded_obd2_df[signals].dropna().describe()
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

def combine_dataframes(decoded_df, signals_found, decoded_obd2_df, obd2_signals_found):

    """
    Explaination: Combine proprietary CAN and OBD2 DataFrames into one. 
    Adds 'CAN_' prefix to proprietary signals and 'OBD2_' to OBD2 signals for clear distinction in analysis and export. 
    """ 

    decoded_df = decoded_df.add_prefix("CAN_")
    decoded_obd2_df = decoded_obd2_df.add_prefix("OBD2_")

    signals_found = list(decoded_df.columns)                                   # used because all signals are included. 
    obd2_signals_found = ["OBD2_" + col for col in obd2_signals_found]         # used because we filtered out the real signals in the decode_obd2 function. 

    combined_df = pd.concat([decoded_df, decoded_obd2_df], axis = 0 )
    combined_signals_found = signals_found + obd2_signals_found

    return combined_df, combined_signals_found

def signal_selector(combined_signals_found):

    # Explaination: Open a GUI listbox for selecting which signals to plot.

    root = tk.Tk()
    root.title("Select Signals to Plot")
    root.geometry("400x500")

    tk.Label(root, text="Select signals to plot: ").pack(pady=5)

    listbox = tk.Listbox(
        root,
        selectmode= tk.MULTIPLE, 
        width=50,
        height= 20
        )
    listbox.pack(pady=5)

    for sig in combined_signals_found:
        listbox.insert(tk.END, sig)

    selected_signals = []

    def on_confirm():
        selected_indices = listbox.curselection()
        for i in selected_indices:
            selected_signals.append(combined_signals_found[i])
        root.quit()

    tk.Button(root, text="Confirm", command = on_confirm).pack(pady=5)
    tk.Button(root, text = "Cancel", command = root.quit).pack(pady=5)

    
    root.mainloop()
    root.destroy()

    print (f"Selected: {selected_signals}")
    
    return selected_signals

def plot_signals(combined_df, signals, title='CAN Data'):

    """
    Explaination: Plot selected signals interactively using Plotly. Each signal gets its own subplot. Vertical spacing scales
    automatically based on number of signals.
    """

    colours = [
        'red', 'blue', 'green', 'indigo',
        'orange', 'purple', 'brown', 'pink', 'magenta', 'olive', 'darkgreen', 'darkblue'
    ]
    
    vertical_spacing = min(0.05, 1 / (len(signals) - 1) - 0.001) if len(signals) > 1 else 0.05
    
    fig = make_subplots(
        rows             = len(signals),
        cols             = 1,
        shared_xaxes     = False,
        subplot_titles   = signals,
        vertical_spacing = vertical_spacing
    )

    for i, sig_name in enumerate(signals):
        sig_data = combined_df[sig_name].dropna()
        colour   = colours[i % len(colours)]                               # cycles through colours

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
        height        = 250* len(signals),
        width         = 500 * len(signals),
        plot_bgcolor  = 'white',
        paper_bgcolor = 'white'
    )

    fig.update_xaxes(
        showgrid  = True,
        gridcolor = 'black',
        gridwidth = 0.1, 
        layer     = 'below traces',
        title_text='Time (seconds)', 
        row=len(signals), 
        col=1
    )
    fig.update_yaxes(
        showgrid  = True,
        gridcolor = 'black',
        gridwidth = 0.1,
        layer     = 'below traces',

    )
    fig.show()
        
def file_save(combined_df, combined_signals_found):

    """
    Explaination: Save decoded signal data to a CSV file. Opens GUI dialogs for folder selection and filename input.
    Only saves real signal columns.
    """
        
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
    
    combined_df[combined_signals_found].to_csv(file_path)
    print(f"Saved to : {file_path}")
    print (f"Number of rows: {len(combined_df)}")
    print (f"Columns : {list(combined_df.columns)}")