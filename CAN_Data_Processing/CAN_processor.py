from asammdf import MDF 
import cantools 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

def load_dbc(dbc_path):
    db = cantools.database.load_file(dbc_path)
    print (f"DBC loaded : {dbc_path}")
    print (f"Messages : {len(db.messages)}")
    return db 

def load_mf4(mf4_path): 
    mdf = MDF(mf4_path)
    raw_df = mdf.to_dataframe()
    raw_df = raw_df.rename(columns={
        'CAN_DataFrame.CAN_DataFrame.ID'         : 'ID',
        'CAN_DataFrame.CAN_DataFrame.DataBytes'  : 'DataBytes',
        'CAN_DataFrame.CAN_DataFrame.DataLength' : 'DataLength',
        'CAN_DataFrame.CAN_DataFrame.Dir'        : 'Dir',
        'CAN_DataFrame.CAN_DataFrame.BusChannel' : 'BusChannel', 
        'CAN_DataFrame.CAN_DataFrame.IDE'        : 'IDE', 
        'CAN_DataFrame.CAN_DataFrame.DLC'        : 'DLC', 
        'CAN_DataFrame.CAN_DataFrame.EDL'        : 'EDL',
        'CAN_DataFrame.CAN_DataFrame.BRS'        : 'BRS'

    })
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

    print (f"Decoded Signals : {len(decoded_df)}")
    print(f"Signals found : {list(decoded_df.columns)}")

    return decoded_df

def plot_signals(decoded_df, signals, title='OBD2 Data'):

    colours = [
        'red', 'blue', 'green', 'indigo',
        'orange', 'purple', 'brown', 'pink', 'magenta', 'olive', 'darkgreen', 'darkblue'
    ]

    fig = make_subplots(
        rows             = len(signals),
        cols             = 1,
        shared_xaxes     = True,
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
        plot_bgcolor  = 'white',
        paper_bgcolor = 'white'
    )

    fig.update_xaxes(
        showgrid  = True,
        gridcolor = 'rgba(128, 128, 128, 0.3)',
        gridwidth = 0.5
    )
    fig.update_yaxes(
        showgrid  = True,
        gridcolor = 'rgba(128, 128, 128, 0.3)',
        gridwidth = 0.5,
        layer     = 'below traces'
    )

    fig.update_xaxes(title_text='Time (seconds)', row=len(signals), col=1)
    fig.show()
        
