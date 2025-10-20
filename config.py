# config.py
CEID_MAP = {11:"Offline", 12:"Local", 13:"Remote", 101:"Alarm Cleared", 102:"Alarm Set", 120:"ID Read", 127:"Loaded to Tool", 131:"Load Complete", 132:"Unload Complete", 136:"Mapping Complete", 141:"Port Status Change", 151:"Magazine Docked", 180:"Request Dock", 181:"Magazine Docked", 182:"Magazine Undocked", 183:"Request Operator Check", 184:"Request Operator Login", 185:"Request Mapping"}
RPTID_MAP = {152:['OpID'], 150:['MagID'], 151:['PortID','MagID','OpID'], 141:['PortID','PortStatus'], 120:['LotID','PanelID'], 121:['LotID','PanelID'], 101:['AlarmID']}
