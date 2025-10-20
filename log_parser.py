# log_parser.py
import re
from io import StringIO
from config import CEID_MAP, RPTID_MAP

def _parse_s6f11_report(full_text: str) -> dict:
    data = {}
    tokens = re.findall(r"<(?:A|U\d)\s\[\d+\]\s(?:'([^']*)'|(\d+))>", full_text)
    flat_values = [s if s else i for s, i in tokens]
    if len(flat_values) < 3: return {}
    try:
        ceid, rptid = int(flat_values[1]), int(flat_values[2])
    except (ValueError, IndexError): return {}
    if ceid in CEID_MAP:
        data['CEID'] = ceid
        if "Alarm" in CEID_MAP.get(ceid, ''): data['AlarmID'] = ceid
    if rptid in RPTID_MAP:
        data['RPTID'] = rptid
        payload = flat_values[3:]
        field_names = RPTID_MAP.get(rptid, [])
        for i, name in enumerate(field_names):
            if i < len(payload): data[name] = payload[i]
    return data

def _parse_s2f49_command(full_text: str) -> dict:
    data = {}
    rcmd = re.search(r"<\s*A\s*\[\d+\]\s*'([A-Z_]{5,})'", full_text)
    if rcmd: data['RCMD'] = rcmd.group(1)
    lotid = re.search(r"'LOTID'\s*>\s*<A\[\d+\]\s*'([^']*)'", full_text, re.IGNORECASE)
    if lotid: data['LotID'] = lotid.group(1)
    panels = re.search(r"'LOTPANELS'\s*>\s*<L\s\[(\d+)\]", full_text, re.IGNORECASE)
    if panels: data['PanelCount'] = int(panels.group(1))
    return data

def parse_log_file(uploaded_file):
    events = []
    if not uploaded_file: return events
    try: lines = StringIO(uploaded_file.getvalue().decode("utf-8")).readlines()
    except: lines = StringIO(uploaded_file.getvalue().decode("latin-1", errors='ignore')).readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        header_match = re.match(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+),\[([^\]]+)\],(.*)", line)
        if not header_match: i += 1; continue
        timestamp, log_type, message_part = header_match.groups()
        msg_match = re.search(r"MessageName=(\w+)|Message=.*?:\'(\w+)\'", message_part)
        msg_name = (msg_match.group(1) or msg_match.group(2)) if msg_match else "N/A"
        event = {"timestamp": timestamp, "msg_name": msg_name}
        if ("Core:Send" in log_type or "Core:Receive" in log_type) and i + 1 < len(lines) and lines[i+1].strip().startswith('<'):
            j = i + 1; block_lines = []
            while j < len(lines) and lines[j].strip() != '.':
                block_lines.append(lines[j]); j += 1
            i = j
            if block_lines:
                full_text = "".join(block_lines)
                details = {}
                if msg_name == 'S6F11': details = _parse_s6f11_report(full_text)
                elif msg_name == 'S2F49': details = _parse_s2f49_command(full_text)
                if details: event['details'] = details
        if 'details' in event:
            events.append(event)
        i += 1
    return events
