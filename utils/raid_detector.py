import time
from collections import defaultdict

join_tracker = defaultdict(list)
message_tracker = defaultdict(list)

JOIN_THRESHOLD = 5
JOIN_WINDOW = 10

SPAM_THRESHOLD = 5
SPAM_WINDOW = 8

MENTION_LIMIT = 5

def check_raid(guild_id):
    now = time.time()
    join_tracker[guild_id] = [t for t in join_tracker[guild_id] if now - t < JOIN_WINDOW]
    return len(join_tracker[guild_id]) >= JOIN_THRESHOLD

def record_join(guild_id):
    join_tracker[guild_id].append(time.time())

def check_spam(user_id):
    now = time.time()
    message_tracker[user_id] = [t for t in message_tracker[user_id] if now - t < SPAM_WINDOW]
    return len(message_tracker[user_id]) >= SPAM_THRESHOLD

def record_message(user_id):
    message_tracker[user_id].append(time.time())

def excessive_mentions(message):
    return len(message.mentions) >= MENTION_LIMIT
