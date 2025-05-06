import os
import pandas as pd
from datetime import datetime
import numpy as np
import re

folder_path = os.path.expanduser("~/Desktop/locomotion_data_csv")
data_records = []

task_order = {
    "1= exploration 3 min (FreeExploration)": 1,
    "2= find elev first time (ExploreTask01)": 2,
    "3= find elev second time (ExploreTask02)": 3,
    "1 (Room \"D -306\")": 4,
    "2 (Room \"A -101\")": 5,
    "3 (Room \"B -208\")": 6,
    "4 (Room \"C -110\")": 7,
    "5 (Nursing 1st Time)": 8,
    "6 (Nursing 2nd Time)": 9,
}

task_starts = {
    "1= exploration 3 min (FreeExploration)": "FreeExploration Started",
    "2= find elev first time (ExploreTask01)": "ExploreTask01_Started",
    "3= find elev second time (ExploreTask02)": "ExploreTask02_Started",
    "1 (Room \"D -306\")": "TaskStart Tofind_Room \"D -306\"",
    "2 (Room \"A -101\")": "TaskStart Tofind_Room \"A -101\"",
    "3 (Room \"B -208\")": "TaskStart Tofind_Room \"B -208\"",
    "4 (Room \"C -110\")": "TaskStart Tofind_Room \"C -110\"",
    "5 (Nursing 1st Time)": "TaskStart Tofind_Nursing Station",
    "6 (Nursing 2nd Time)": "TaskStart Tofind_Nursing Station Again",
}

task_ends = {
    "1= exploration 3 min (FreeExploration)": "FreeExplorationEnd",
    "2= find elev first time (ExploreTask01)": "ExploreTask01_Ended",
    "3= find elev second time (ExploreTask02)": "ExploreTask02_Ended",
}

completion_event = "WellDoneWidgetPressed"
zone_ad_targets = [
    'ZoneMarker_Start_Zone "A"',
    'ZoneMarker_Start_Zone "B"',
    'ZoneMarker_Start_Zone "C"',
    'ZoneMarker_Start_Zone "D"',
]

def parse_time(t):
    try:
        return datetime.strptime(t.strip(), "%I:%M:%S %p")
    except:
        return None

for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        parts = filename.split("_")
        pid = int(parts[0])
        level = parts[1]
        scene_type = parts[2].replace(".csv", "")
        filepath = os.path.join(folder_path, filename)

        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        if not all(col in df.columns for col in ["Time", "ms", "EventText"]):
            continue

        pointing_rotations = []
        for _, row in df.iterrows():
            if isinstance(row.get("EventAnswer"), str) and "Arrow Rotation:P=" in row["EventAnswer"]:
                match = re.search(r"Rotation:P=([-+]?[0-9]*\.?[0-9]+)", row["EventAnswer"])
                if match:
                    pointing_rotations.append(float(match.group(1)))

        estimated_distances = df[df["EventText"] == "DistanceReported(inFeet)"]["EventAnswer"].tolist()
        point_idx = 0
        dist_idx = 0
        ex_point_idx = 0
        task6_found = False

        for task_name, start_event in task_starts.items():
            if ("Exploration" in scene_type and "Task-Based" in task_name) or ("TaskBased" in scene_type and "Exploration" in task_name):
                continue

            end_event = task_ends.get(task_name, completion_event)

        
            if "Room" in start_event:
                room_name = start_event.split("Room")[-1].strip().strip('"')
                start_rows = df[df["EventText"].astype(str).str.contains("TaskStart") &
                                df["EventText"].astype(str).str.contains(room_name)]
            else:
                start_rows = df[df["EventText"] == start_event]

            if start_rows.empty:
                if task_name == "6 (Nursing 2nd Time)" and "TaskBased" in scene_type:
                    data_records.append({
                        "PID": pid,
                        "Level (teleportation type)": level,
                        "Scene Type": "Task-Based",
                        "Task": task_name,
                        "TimeSpend": np.nan,
                        "Distance Covered": np.nan,
                        "Room Sign Frequency": np.nan,
                        "Roomsign 'time' watched": np.nan,
                        "Zone Sign Frequency": np.nan,
                        "Zone Markers A-D Frequency": np.nan,
                        "Pointing Task": np.nan,
                        "Estimated Distance Reported": np.nan
                    })
                continue

            start_idx = start_rows.index[0]
            start_time = parse_time(df.loc[start_idx, "Time"])
            start_ms = df.loc[start_idx, "ms"]

            if end_event in task_ends.values():
                end_rows = df[(df.index > start_idx) & (df["EventText"] == end_event)]
            else:
                end_rows = df[(df.index > start_idx) & (df["EventText"] == completion_event)]

            end_idx = end_rows.index[0] if not end_rows.empty else df.index[-1]
            end_time = parse_time(df.loc[end_idx, "Time"])
            end_ms = df.loc[end_idx, "ms"] if not end_rows.empty else None

            if start_time and end_time and pd.notna(start_ms) and pd.notna(end_ms):
                time_delta = (end_time - start_time).total_seconds()
                ms_delta = (end_ms - start_ms) / 1000.0
                time_spent = time_delta + ms_delta
            else:
                time_spent = np.nan

            task_df = df.loc[start_idx:end_idx]

            try:
                x1, y1 = df.loc[start_idx, "xHead"], df.loc[start_idx, "yHead"]
                x2, y2 = df.loc[end_idx, "xHead"], df.loc[end_idx, "yHead"]
                distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            except:
                distance = np.nan

            room_freq = task_df["EventText"].astype(str).str.contains("RoomMarker_Start").sum()
            zone_freq = task_df["EventText"].astype(str).str.contains("ZoneMarker_Start").sum()
            zone_ad_freq = task_df["EventText"].isin(zone_ad_targets).sum()

            room_time_total = 0
            start_time_point = None
            for _, row in task_df.iterrows():
                if isinstance(row["EventText"], str):
                    if row["EventText"].startswith("RoomMarker_Start"):
                        start_time_point = row["ms"]
                    elif row["EventText"].startswith("RoomMarker_End") and start_time_point is not None:
                        end_time_point = row["ms"]
                        duration = (end_time_point - start_time_point) / 1000.0
                        if duration >= 0:
                            room_time_total += duration
                        start_time_point = None

            
            if "Exploration" in scene_type:
                if "1= exploration" in task_name:
                    pointing = np.nan
                else:
                    pointing = pointing_rotations[ex_point_idx] if ex_point_idx < len(pointing_rotations) else np.nan
                    ex_point_idx += 1
                if "2= find elev" in task_name:
                    est_dist = float(estimated_distances[0]) if len(estimated_distances) >= 1 else np.nan
                elif "3= find elev" in task_name:
                    est_dist = float(estimated_distances[1]) if len(estimated_distances) >= 2 else np.nan
                else:
                    est_dist = np.nan
            else:
                
                if task_name in ["5 (Nursing 1st Time)", "6 (Nursing 2nd Time)"]:
                    wp_idx = df[(df.index > start_idx) & (df["EventText"] == completion_event)].index
                    rotation = np.nan
                    if not wp_idx.empty:
                        search_idx = wp_idx[0]
                        for _, row in df.loc[search_idx:].iterrows():
                            if isinstance(row.get("EventAnswer"), str) and "Arrow Rotation:P=" in row["EventAnswer"]:
                                match = re.search(r"Rotation:P=([-+]?[0-9]*\.?[0-9]+)", row["EventAnswer"])
                                if match:
                                    rotation = float(match.group(1))
                                    break
                    pointing = rotation
                else:
                    pointing = pointing_rotations[point_idx] if point_idx < len(pointing_rotations) else np.nan
                    point_idx += 1
                est_dist = float(estimated_distances[dist_idx]) if dist_idx < len(estimated_distances) else np.nan
                dist_idx += 1

            data_records.append({
                "PID": pid,
                "Level (teleportation type)": level,
                "Scene Type": "Exploration" if "Exploration" in scene_type else "Task-Based",
                "Task": task_name,
                "TimeSpend": time_spent,
                "Distance Covered": distance,
                "Room Sign Frequency": room_freq,
                "Roomsign 'time' watched": room_time_total,
                "Zone Sign Frequency": zone_freq,
                "Zone Markers A-D Frequency": zone_ad_freq,
                "Pointing Task": pointing,
                "Estimated Distance Reported": est_dist
            })

df_out = pd.DataFrame(data_records)
df_out["TaskOrder"] = df_out["Task"].map(task_order)
df_out = df_out.sort_values(by=["PID", "TaskOrder"])
df_out.drop(columns=["TaskOrder"], inplace=True)

output = os.path.expanduser("~/Desktop/VR_Locomotion_Cleaned_Data.csv")
df_out.to_csv(output, index=False)
print(f"Final data saved to: {output}")
