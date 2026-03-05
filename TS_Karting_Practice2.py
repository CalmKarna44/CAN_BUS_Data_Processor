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

# Filter the string data to seconds using datetime.

def clean_input_laps(laps):
    laps_clean = []
    for t in laps:
        if ":" not in t:
            t = "0:" + t
        laps_dt = datetime.strptime(t, "%M:%S.%f")
        total_seconds = laps_dt.minute * 60 + laps_dt.second + laps_dt.microsecond / 1e6
        laps_clean.append(total_seconds)
    return np.array(laps_clean)

laps_clean = clean_input_laps(laps)
print(laps_clean)

# Fast Lap Filter Function

def filter_fast_laps(lap_times):
    laps_fast = np.full(len(laps_clean), np.nan)
    laps_fast[laps_clean <= 40] = laps_clean[laps_clean <= 40]
    return np.array(laps_fast)

laps_fast = filter_fast_laps(laps_clean)

# Made a dictionary to store stats and easily use

def stats(laps_times):
    return {
        "fastest_lap": np.nanmin(laps_fast),
        "fastest_lap_number": np.nanargmin(laps_fast)+1,
        "avg": np.nanmean(laps_fast),
        "std_deviation": np.nanstd(laps_fast)
    }

get_stats = stats(laps_fast)

# Printing Statistics

print("Average:", round(get_stats["avg"], 3))
print("Fastest Lap Number:", get_stats["fastest_lap_number"])
print("Fastest:", get_stats["fastest_lap"])
print("Consistency:", round(get_stats["std_deviation"], 3))

# Plotting of results.

fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
plt.xticks(lap_numbers)

# First Subplot with all the laps of the session

axes[0].plot(lap_numbers, laps_clean, linestyle="--",
             marker="o", label="All Laps")
axes[0].set_ylabel("Lap Time (s)")
axes[0].set_title("All Laps")
axes[0].scatter(get_stats["fastest_lap_number"], get_stats["fastest_lap"], color="gold",
                edgecolor="black", s=90, zorder=5, label=f"Fastest Lap= {get_stats["fastest_lap"]:.3f} s")
axes[0].annotate(f"{get_stats["fastest_lap"]:.3f} s", (get_stats["fastest_lap_number"],
                 get_stats["fastest_lap"]), fontweight="bold", textcoords="offset points", xytext=(-10, 10))
axes[0].legend()
axes[0].grid(True)

# Second Subplot with only fast laps of the session

mask = ~np.isnan(laps_fast)
axes[1].plot(lap_numbers[mask], laps_fast[mask], color="red",
             marker="x", label="Fast laps (<= 40s)")
axes[1].axhline(get_stats["avg"], linestyle="--", color="black",
                label=f"Average Pace: {get_stats["avg"]:.3f}s")
axes[1].set_ylabel("Lap Time (s)")
axes[1].set_xlabel("Lap Numbers")
axes[1].set_title("Fast Laps (<= 40s)")
axes[1].scatter(get_stats["fastest_lap_number"], get_stats["fastest_lap"], marker="x",
                color="gold", s=90, zorder=5, label=f"Fastest Lap= {get_stats["fastest_lap"]:.3f} s")
axes[1].annotate(f"{get_stats["fastest_lap"]:.3f} s", (get_stats["fastest_lap_number"],
                 get_stats["fastest_lap"]), fontweight="bold", textcoords="offset points", xytext=(-60, -5))
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.show()
