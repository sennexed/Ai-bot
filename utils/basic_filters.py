import re
import time

SPAM_LIMIT = 6
SPAM_WINDOW = 5
MENTION_LIMIT = 5

user_message_cache = {}

def is_spam(user_id):
    now = time.time()
    user_message_cache.setdefault(user_id, [])
    user_message_cache[user_id] = [
        t for t in user_message_cache[user_id]
        if now - t < SPAM_WINDOW
    ]
    user_message_cache[user_id].append(now)
    return len(user_message_cache[user_id]) >= SPAM_LIMIT


def excessive_mentions(message):
    return len(message.mentions) >= MENTION_LIMIT


def repeated_text(content):
    words = content.lower().split()
    if len(words) < 6:
        return False
    return len(set(words)) <= 2


def character_flood(content):
    return re.search(r"(.)\1{8,}", content) is not None


def contains_blacklisted_link(content):
    blacklisted = ["grabify", "iplogger", "free-nitro"]
    return any(bad in content.lower() for bad in blacklisted)


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text
