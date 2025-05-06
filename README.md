# VR Locomotion Data Cleaning

This repository contains a Python script for processing and cleaning VR locomotion data collected from immersive navigation tasks. The script is designed to extract per-task behavioral metrics for each participant to support downstream analysis of spatial orientation and wayfinding behavior in VR.

## Features

- **Task Segmentation:** Identifies task start and end points for 3 Exploration and 6 Task-Based tasks.
- **Time Metrics:** Calculates time spent per task using timestamps and millisecond precision.
- **Distance Metrics:** Computes distance covered per task using Euclidean distance from xHead/yHead coordinates.
- **Sign Frequencies:**
  - Room Sign Frequency
  - Zone Sign Frequency
  - Zone Markers A–D Frequency
- **Room Sign Viewing Time:** Aggregates time spent looking at room signs per task.
- **Pointing Task Analysis:** Extracts the pitch angle ("P") from Arrow Rotation strings in the EventAnswer field.
- **Estimated Distance Reported:** Parses self-reported navigation estimates from EventAnswer for both Exploration and Task-Based tasks.

## Input

- Folder of `.csv` files exported from VR session logs.
- Each file includes timestamped events with metadata like position, markers, and user inputs.

## Output

- A single cleaned `.csv` dataset with one row per participant-task, containing all computed metrics.
- Output is sorted by Participant ID and task order.

## Usage

1. Place all raw session `.csv` files in a folder (e.g., `~/Desktop/locomotion_data_csv`).
2. Update the `folder_path` variable in the script if needed.
3. Run the script with:
   ```bash
   python vr_locomotion_cleaning.py
  
4. Cleaned data will be saved to your desktop as VR_Locomotion_Cleaned_Data.csv.

Notes
Missing tasks (e.g., if a participant did not complete Task 6) are still included with NaN values.

Script handles inconsistencies in log formatting and performs validation on all fields.
