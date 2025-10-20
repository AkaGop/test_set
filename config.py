# config.py
"""
Single source of truth for all static configuration data.
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
    122: ['Timestamp', 'LotID', 'SourcePortID', 'DestPortID', 'PanelList'],
    11:  ['Timestamp', 'ControlState'],
    101: ['Timestamp', 'AlarmIDValue'],
}
