from CAN_processor import load_dbc, load_mf4, decode_obd2,filter_obd2, plot_signals, file_save

DBC_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\obd2-dbc\CSS-Electronics-11-bit-OBD2-v2.2.dbc"
MF4_PATH = r"C:\Users\dell\Desktop\MBGP Mentoring\Programming\Excel Data\obd2-pack-v5\obd2-sample-data\Mercedes E350 2010\00000001.MF4"

db = load_dbc(DBC_PATH)
raw_df = load_mf4(MF4_PATH)

obd2_df = filter_obd2(raw_df)

decoded_df = decode_obd2(obd2_df, db)

signals_to_plot = [
'S01PID10_MAFAirFlowRate', 
'S01PID0B_IntakeManiAbsPress', 
'S01PID0C_EngineRPM', 
'S01PID0D_VehicleSpeed', 
'S01PID11_ThrottlePosition', 
'S01PID05_EngineCoolantTemp', 
'S01PID2F_FuelTankLevel'
]

plot_signals(decoded_df, signals_to_plot, title='Mercedes E350 OBD2 Data')

file_save(decoded_df)
