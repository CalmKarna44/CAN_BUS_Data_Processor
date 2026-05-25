from CAN_processor import select_file, load_dbc, load_obd2_dbc, load_mf4, decode_raw_can, filter_obd2, decode_obd2, signal_stats ,combine_dataframes, signal_selector, plot_signals, file_save


# Configuration — update paths for your vehicle
DBC_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\proprietary-can-dbc\Stellantis\stellantis_dasm.dbc"

OBD2_DBC_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\obd2-dbc\CSS-Electronics-11-bit-OBD2-v2.2.dbc"

# Use of the code
db = load_dbc(DBC_PATH)

obd2_db = load_obd2_dbc(OBD2_DBC_PATH)

mf4_path = select_file()

if mf4_path:
    # Load raw data
    raw_df = load_mf4(mf4_path)
    
    # Decode proprietary CAN signals
    decoded_df, signals_found = decode_raw_can(raw_df, db)

    # Decode OBD2 signals
    obd2_df = filter_obd2(raw_df)

    if obd2_df is not None:
        decoded_obd2_df, obd2_signals_found = decode_obd2(obd2_df, obd2_db)

    if decoded_df is None and decoded_obd2_df is not None:
        combined_df = decoded_obd2_df.add_prefix("OBD2_")
        combined_signals_found = ["OBD2_" + col for col in obd2_signals_found]

    elif decoded_df is not None and decoded_obd2_df is None:
        combined_df = decoded_df.add_prefix("CAN_")
        combined_signals_found = list(combined_df.columns) 

    elif decoded_df is not None and decoded_obd2_df is not None: 
        combined_df, combined_signals_found = combine_dataframes(decoded_df, signals_found, decoded_obd2_df, obd2_signals_found)

    else: 
        print("No data decoded from either dbc - Exiting!")
        exit()

     # Statistical summary of OBD2 Data
    stats = signal_stats(decoded_obd2_df, obd2_signals_found)
    
    # Select signals and plot
    signals_to_plot = signal_selector(combined_signals_found)

    signal_plotting = plot_signals(combined_df, signals_to_plot, title='Renault Zoe CAN Data')

    # Save to CSV
    file_save(combined_df, combined_signals_found)
