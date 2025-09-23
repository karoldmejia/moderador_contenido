import pytest

from src.preprocessing import (
    extract_mentions,
    extract_hashtags,
    extract_urls,
    extract_emojis,
    normalize_text,
)

def test_extract_mentions_single():
    text = "Hello @karol!"
    assert extract_mentions(text) == ["@karol"]

def test_extract_mentions_multiple():
    text = "Hi @ana and @juan!"
    assert extract_mentions(text) == ["@ana", "@juan"]

def test_extract_mentions_none():
    text = "No mentions here"
    assert extract_mentions(text) == []

# -----------------------

def test_extract_hashtags_single():
    text = "I love #Python"
    assert extract_hashtags(text) == ["#Python"]

def test_extract_hashtags_multiple():
    text = "Working with #AI and #ML"
    assert extract_hashtags(text) == ["#AI", "#ML"]

def test_extract_hashtags_none():
    text = "Nothing special"
    assert extract_hashtags(text) == []

# -----------------------

def test_extract_urls_single():
    text = "Check this out: https://example.com"
    assert extract_urls(text) == ["https://example.com"]

def test_extract_urls_multiple():
    text = "Links: http://test.com https://openai.com"
    assert extract_urls(text) == ["http://test.com", "https://openai.com"]

def test_extract_urls_none():
    text = "No links here"
    assert extract_urls(text) == []

# -----------------------

def test_extract_emojis_single():
    text = "Hello 😎"
    assert extract_emojis(text) == ["😎"]

def test_extract_emojis_multiple():
    text = "Cool 😎🔥"
    assert set(extract_emojis(text)) == {"😎", "🔥"}  # orden no siempre garantizado

def test_extract_emojis_none():
    text = "Just text"
    assert extract_emojis(text) == []

# -----------------------

def test_normalize_text_basic():
    text = "   Hello   World   "
    assert normalize_text(text) == "hello world"

def test_normalize_text_mixed_case():
    text = "PyThOn Is CoOl"
    assert normalize_text(text) == "python is cool"

def test_normalize_text_with_tabs_and_newlines():
    text = "Hello\t\nWorld"
    assert normalize_text(text) == "hello world"
