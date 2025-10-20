# config.py
"""
Single source of truth for all static configuration data, including Alarm Classifications.
"""
CEID_MAP = {
    11: "Equipment Offline", 12: "Control State Local", 13: "Control State Remote",
    16: "PP-SELECT Changed", 30: "Process State Change", 101: "Alarm Cleared",
    102: "Alarm Set", 18: "AlarmSet", 113: "AlarmSet", 114: "AlarmSet", 
    120: "IDRead", 121: "UnloadedFromMag/LoadedToTool", 127: "LoadedToTool",
    131: "LoadToToolCompleted", 132: "UnloadFromToolCompleted", 136: "MappingCompleted",
    141: "PortStatusChange", 151: "MagazineDocked", 180: "RequestMagazineDock",
    181: "MagazineDocked", 182: "MagazineUndocked", 183: "RequestOperatorIdCheck",
    184: "RequestOperatorLogin", 185: "RequestMappingCheck",
}

RPTID_MAP = {
    152: ['Timestamp', 'OperatorID'],
    150: ['Timestamp', 'MagazineID'],
    151: ['Timestamp', 'PortID', 'MagazineID', 'OperatorID'],
    141: ['Timestamp', 'PortID', 'PortStatus'],
    120: ['Timestamp', 'LotID', 'PanelID', 'Orientation', 'ResultCode', 'SlotID'],
    121: ['Timestamp', 'LotID', 'PanelID', 'SlotID'],
    11:  ['Timestamp', 'ControlState'],
    101: ['Timestamp', 'AlarmIDValue'],
}

# --- START OF HIGHLIGHTED CHANGE ---
# This list defines which alarms are considered "hard faults" that stop the process.
# Hex values from the PDF have been converted to decimal. 0x10F0 -> 4336
CRITICAL_ALARM_IDS = [
    1, 2, 190, 191, 192, 193, 194,  # System & Safety
    1050, 1051, 1052, 1053, 1055,   # Panel Motion & Homing
    4336, 4337,                     # HNC & Fork Errors
    5458, 5459, 5460,               # Panel Pick/Place Errors
    8192, 8193, 8194, 8195, 8196, 8197, # Port 1 Driver/Inverter Errors
    12288, 12289, 12290, 12291, 12292, 12293 # Port 2 Driver/Inverter Errors
]

# This dictionary translates alarm codes into human-readable text.
ALARM_MAP = {
    1: "CPU error", 2: "SafetyPLC error", 18: "Safety door open", 113: "HNC error",
    114: "Fork Coll.Detect error", 131: "Panel pick NG", 190: "Emergency stop",
    191: "Safety door open", 4336: "HNC error", 4337: "Fork Coll.Detect error",
    5458: "Panel pick NG"
    # Add more mappings from Error_code.txt as needed
}
# --- END OF HIGHLIGHTED CHANGE ---
