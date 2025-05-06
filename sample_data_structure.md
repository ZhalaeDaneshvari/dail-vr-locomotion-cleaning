# Sample Data Structure for VR Locomotion Logs

This script expects `.csv` files exported from the VR experiment logs with the following structure:

## Required Columns

| Column Name | Description |
|-------------|-------------|
| Time        | Timestamp in format like `3:57:36 PM` |
| ms          | Milliseconds timestamp (used for precise time deltas) |
| EventText   | Description of the logged event (e.g., "FreeExploration Started", "RoomMarker_Start_...") |
| EventAnswer | Values associated with the event (e.g., "Arrow Rotation:P=-3.3 Y=..." or distance estimates) |
| xHead       | Participant's head X position |
| yHead       | Participant's head Y position |

## File Naming Convention

Each `.csv` should follow this format:

PID_Level_SceneType_Date_Hash.csv

- **PID**: Participant ID (e.g., `012`)
- **Level**: Teleportation type (e.g., `L3`, `L4`)
- **SceneType**: Either `Exploration` or `TaskBased`
- **Date**: Date of session (e.g., `Aug 21, 2024`)
- **Hash**: Unique hash identifier

Example: 012_L4_Exploration_Aug 21, 2024_ks3J85zzMT.csv 

Note: Participant data should not be uploaded to this repository.
