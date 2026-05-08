from CAN_processor import select_file, load_dbc, load_obd2_dbc, load_mf4, decode_raw_can, filter_obd2, decode_obd2, signal_stats ,combine_dataframes, signal_selector, plot_signals, file_save

DBC_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\proprietary-can-dbc\Renault Zoe\rz.dbc"

OBD2_DBC_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\obd2-dbc\CSS-Electronics-29-bit-OBD2-v2.2.dbc"

db = load_dbc(DBC_PATH)

obd2_db = load_obd2_dbc(OBD2_DBC_PATH)

mf4_path = select_file()

if mf4_path:
    raw_df = load_mf4(mf4_path)
    print(f"Unique IDs in raw_df : {raw_df['ID'].unique()}")
    
    decoded_df, signals_found = decode_raw_can(raw_df, db)

    obd2_df = filter_obd2(raw_df)

    decoded_obd2_df, obd2_signals_found = decode_obd2(obd2_df, obd2_db)

    stats = signal_stats(decoded_obd2_df, obd2_signals_found)

    combined_df, combined_signals_found = combine_dataframes(decoded_df, signals_found, decoded_obd2_df, obd2_signals_found)
    
    signals_to_plot = signal_selector(combined_signals_found)

    signal_plotting = plot_signals(combined_df, signals_to_plot, title='Renault Zoe CAN Data')

    file_save(combined_df, combined_signals_found)
