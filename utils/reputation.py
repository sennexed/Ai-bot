SEVERITY_WARN = 40
SEVERITY_TIMEOUT = 70
SEVERITY_BAN = 90

def calculate_action(severity, previous_count):
    if severity >= SEVERITY_BAN:
        return "ban"

    if severity >= SEVERITY_TIMEOUT:
        return "timeout"

    if severity >= SEVERITY_WARN or previous_count >= 2:
        return "warn"

    return None


def update_reputation(current_rep, severity):
    return current_rep - (severity // 10)
