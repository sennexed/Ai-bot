import time

join_tracker = []

def detect_raid():
    global join_tracker
    now = time.time()

    join_tracker = [t for t in join_tracker if now - t < 10]
    join_tracker.append(now)

    return len(join_tracker) >= 5
