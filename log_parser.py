# log_parser.py
import re
from io import StringIO
from config import CEID_MAP, RPTID_MAP
from parser_utils import tokenize, build_tree

def _parse_s6f11_report(full_text: str) -> dict:
    """Final, robust parser using a hierarchical tree-based approach."""
    data = {}
    tokens = tokenize(full_text)
    tree = build_tree(tokens)
    
    try:
        # According to SECS-II standard for S6F11
        s6f11_body = tree[0]
        ceid = int(s6f11_body[1])
        report_list = s6f11_body[2]
        
        # The first report in the list
        rptid = int(report_list[0][0])
        payload = report_list[0][1]

        if ceid in CEID_MAP: data['CEID'] = ceid
        if "Alarm" in CEID_MAP.get(ceid, ''): data['AlarmID'] = ceid
        
        if rptid in RPTID_MAP:
            data['RPTID'] = rptid
            field_names = RPTID_MAP.get(rptid, [])
            # Separate timestamp from other data fields
            if field_names[0] == 'Timestamp':
                data['ReportTimestamp'] = payload[0]
                # The rest of the payload is the actual data
                data_payload = payload[1:]
                field_names = field_names[1:]
            else:
                data_payload = payload
            
            for i, name in enumerate(field_names):
                if i < len(data_payload):
                    data[name] = data_payload[i]
    except (IndexError, ValueError):
        # Gracefully fail if the message structure is unexpected
        return {}
        
    return data

def _parse_s2f49_command(full_text: str) -> dict:
    """Parses S2F49 Remote Commands."""
    data = {}
    rcmd_match = re.search(r"<\s*A\s*\[\d+\]\s*'([A-Z_]{5,})'", full_text)
    if rcmd_match: data['RCMD'] = rcmd_match.group(1)
    lotid_match = re.search(r"'LOTID'\s*>\s*<A\[\d+\]\s*'([^']*)'", full_text, re.IGNORECASE)
    if lotid_match: data['LotID'] = lotid_match.group(1)
    panels_match = re.search(r"'LOTPANELS'\s*>\s*<L\s\[(\d+)\]", full_text, re.IGNORECASE)
    if panels_match: data['PanelCount'] = int(panels_match.group(1))
    return data

def parse_log_file(uploaded_file):
    events = []
    if not uploaded_file: return events
    try: lines = StringIO(uploaded_file.getvalue().decode("utf-8")).readlines()
    except: lines = StringIO(uploaded_file.getvalue().decode("latin-1", errors='ignore')).readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i+= 1; continue
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
