# config.py
"""
Single source of truth for all static configuration data, including Alarm Classifications.
"""
CEID_MAP = {
    # ... (content is the same as the last step)
}
RPTID_MAP = {
    # ... (content is the same as the last step)
}
ALARM_MAP = {
    # ... (content is the same as the last step)
}

# --- START OF HIGHLIGHTED CHANGE ---
# This list defines which alarms are considered "hard faults" that stop the process.
# All other alarms will be treated as "soft warnings."
CRITICAL_ALARM_IDS = [
    # System/Safety
    1, 2, 190, 191, 192, 193, 194,
    # HNC/Fork
    4336, 4337,
    # Panel Motion
    1050, 1051, 1052, 1055, 5458, 5459, 5460,
    # Timeouts that stop a process
    5472, 5473, 5474, 5475, 5476, 5477,
    # Inverter/Driver Errors
    8192, 8193, 8194, 8195, 8196, 8197,
    12288, 12289, 12290, 12291, 12292, 12293,
]
# --- END OF HIGHLIGHTED CHANGE ---
