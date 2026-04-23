from CAN_processor import select_file, load_dbc, load_mf4, decode_obd2,filter_obd2, signal_stats , plot_signals, file_save

DBC_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\obd2-dbc\CSS-Electronics-11-bit-OBD2-v2.2.dbc"

db = load_dbc(DBC_PATH)

mf4_path = select_file()

if mf4_path:
    raw_df = load_mf4(mf4_path)
    print(f"Unique IDs in raw_df : {raw_df['ID'].unique()}")
    
    obd2_df = filter_obd2(raw_df)
    if obd2_df is None: 
        exit()

    decoded_df, signals_found = decode_obd2(obd2_df, db)

    stats = signal_stats(decoded_df, signals_found)

    plot_signals(decoded_df, signals_found, title='Opel Astra (2014) OBD2 Data')

    file_save(decoded_df, signals_found)
