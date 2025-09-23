import re

def extract_mentions(text):
    """Detects mentions like @user"""
    return re.findall(r'@\w+', text)

def extract_hashtags(text):
    """Detects hashtags like #topic"""
    return re.findall(r'#\w+', text)

def extract_urls(text):
    """Detects URLs http or https"""
    return re.findall(r'https?://\S+', text)

def extract_emojis(text):
    """Detects individual emojis (improved version using Unicode ranges)."""
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "]", flags=re.UNICODE
    )
    return emoji_pattern.findall(text)


def normalize_text(text):
    """Converts to lowercase and removes extra spaces"""
    return re.sub(r'\s+', ' ', text.strip().lower())
