def parse_timeline(timeline_text):
    """
    Parses a newline-separated timeline into a list of events.
    Expected format: [Date/Time] - Description
    """
    if not timeline_text:
        return []
    
    events = []
    lines = timeline_text.strip().split('\n')
    for line in lines:
        if '-' in line:
            parts = line.split('-', 1)
            events.append({
                'time': parts[0].strip(),
                'description': parts[1].strip()
            })
        else:
            events.append({
                'time': '',
                'description': line.strip()
            })
    return events

def format_date(date_str):
    # Add date formatting if needed later
    return date_str
