import re


def parse_slack_messages(text: str):
    messages = []
    patterns = [
        r"^\[(.*?)\]\s*(.*?):\s*(.*)$",
        r"^(\d{1,2}:\d{2})\s+(.*?):\s*(.*)$",
        r"^(.*?):\s*(.*)$",
    ]

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matched = None
        for pattern in patterns:
            match = re.match(pattern, line)
            if match and len(match.groups()) == 3:
                matched = {
                    "time": match.group(1).strip(),
                    "user": match.group(2).strip(),
                    "text": match.group(3).strip(),
                }
                break
            if match and len(match.groups()) == 2:
                matched = {
                    "time": "",
                    "user": match.group(1).strip(),
                    "text": match.group(2).strip(),
                }
                break

        if matched:
            messages.append(matched)
        elif messages:
            messages[-1]["text"] += " " + line
        else:
            messages.append({"time": "", "user": "unknown", "text": line})

    return messages


def chunk_slack_messages(text: str, chunk_size: int = 12):
    messages = parse_slack_messages(text)
    return [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]


def chunk_to_text(chunk):
    rows = []
    for message in chunk:
        time = message.get("time", "")
        user = message.get("user", "unknown")
        text = message.get("text", "")
        prefix = f"[{time}] " if time else ""
        rows.append(f"{prefix}{user}: {text}")
    return "\\n".join(rows)
