import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

laps = [
    "47.56",
    "46.413",
    "43.45",
    "35.853",
    "35.494",
    "34.875",
    "35.608",
    "34.97",
    "35.651",
    "35.152",
    "35.634",
    "35.35",
    "36.221",
    "57.78",
    "36.562",
    "03:48.2",
    "40.613",
    "01:14.8",
    "36.482",
    "36.744",
]

lap_numbers = np.array(range(1, len(laps) + 1))
laps_clean = []

for t in laps:
    if ":" not in t:
        t = "0:" + t
    laps_dt = datetime.strptime(t, "%M:%S.%f")
    total_seconds = laps_dt.minute * 60 + laps_dt.second + laps_dt.microsecond / 1e6
    laps_clean.append(total_seconds)

laps_clean = np.array(laps_clean)
print(laps_clean)

laps_fast = np.full(len(laps_clean), np.nan)
laps_fast[laps_clean <= 40] = laps_clean[laps_clean <= 40]
fastest_lap = round(np.nanmin(laps_fast), 3)
fastest_lap_number = np.nanargmin(laps_fast)+1

print("Average:", round(np.mean(laps_fast), 3))  # Printing avg pace
print("Fastest Lap Number:", fastest_lap_number)  # Fastest lap number
print("Fastest:", fastest_lap)   # Fastest Lap Time
# Standard Deviation of laptime
print("Consistency:", round(np.nanstd(laps_fast), 3))

# plt.figure()
# plt.plot(lap_numbers, laps_clean, marker='o', label='All laps')
# plt.xlabel("Lap Number")
# plt.ylabel("Lap Time (s)")
# plt.title("All Laps")
# plt.xticks(lap_numbers)
# plt.legend()
# plt.grid(True)
# plt.show()

# plt.figure()
# mask = ~np.isnan(laps_fast)
# plt.plot(lap_numbers[mask], laps_fast[mask],
#          marker="x", label='Fast laps (≤40s)')
# plt.axhline(np.nanmean(laps_fast), linestyle="--",
#             label=f"Average Pace: {np.nanmean(laps_fast):.3f} s")
# plt.xlabel("Lap Number")
# plt.ylabel("Lap Time (s)")
# plt.title("Fast laps (<= 40s)")
# plt.xticks(lap_numbers)
# plt.legend()
# plt.grid(True)
# plt.show()

mask = ~np.isnan(laps_fast)
fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
plt.xticks(lap_numbers)

axes[0].plot(lap_numbers, laps_clean, linestyle="--",
             marker="o", label="All Laps")
axes[0].scatter(fastest_lap_number, fastest_lap, color="gold", edgecolor="black",
                s=90, zorder=5, label=f"Fastest Lap= {fastest_lap:.3f} s")
axes[0].annotate(f"{fastest_lap:.3f} s", (fastest_lap_number, fastest_lap),
                 fontweight="bold", textcoords="offset points", xytext=(-10, 10))
axes[0].set_ylabel("Lap Time (s)")
axes[0].set_title("All Laps")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(lap_numbers[mask], laps_fast[mask], color="red",
             marker="x", label="Fast laps (<= 40s)")
axes[1].axhline(np.nanmean(laps_fast), linestyle="--", color="black",
                label=f"Average Pace: {np.nanmean(laps_fast):.3f}s")
axes[1].scatter(fastest_lap_number, fastest_lap, marker="x", color="gold", edgecolor="black",
                s=90, zorder=5, label=f"Fastest Lap= {fastest_lap:.3f} s")
axes[1].annotate(f"{fastest_lap:.3f} s", (fastest_lap_number, fastest_lap),
                 fontweight="bold", textcoords="offset points", xytext=(-60, -5))
axes[1].set_ylabel("Lap Time (s)")
axes[1].set_xlabel("Lap Numbers")
axes[1].set_title("Fast Laps (<= 40s)")
axes[1].legend()
axes[1].grid(True)


plt.tight_layout()
plt.show()
