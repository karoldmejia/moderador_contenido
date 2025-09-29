import pytest
from src.preprocessing import RegexTokenizer
from pathlib import Path

@pytest.fixture
def tokenizer():
    keywords_file = Path(__file__).parent.parent / "src" / "data" / "keywords.json"
    return RegexTokenizer(keywords_file=keywords_file)

# -------------------------
#  1. Unit tests
# -------------------------
def test_badwords(tokenizer):
    tokens = tokenizer.tokenize("stupid")
    assert tokens == ["BADWORD"]

def test_sexwords(tokenizer):
    tokens = tokenizer.tokenize("porn")
    assert tokens == ["SEXWORD"]

def test_violence(tokenizer):
    tokens = tokenizer.tokenize("kill")
    assert tokens == ["VIOLENCE"]

def test_spamwords(tokenizer):
    tokens = tokenizer.tokenize("buy now")
    assert tokens == ["SPAMWORD"]

def test_fakeclaims(tokenizer):
    tokens = tokenizer.tokenize("miracle cure")
    assert tokens == ["FAKECLAIM"]

def test_politics(tokenizer):
    tokens = tokenizer.tokenize("democrats")
    assert tokens == ["POLITIC"]

def test_pronouns(tokenizer):
    tokens = tokenizer.tokenize("i you")
    assert tokens == ["PRONOUN_SELF", "PRONOUN_OTHER"]

def test_normal_word(tokenizer):
    tokens = tokenizer.tokenize("hello world")
    assert tokens == ["WORD", "WORD"]

# -------------------------
# 2. Emojis
# -------------------------
def test_good_emoji(tokenizer):
    tokens = tokenizer.tokenize("😀 😃")
    assert tokens == ["EMOJI", "EMOJI"]

def test_bad_emoji(tokenizer):
    tokens = tokenizer.tokenize("💀 💥")
    assert tokens == ["NEG_EMOJI", "EMOJI"]

def test_mixed_emojis(tokenizer):
    tokens = tokenizer.tokenize("😀 💀 😃 💥")
    assert tokens == ["EMOJI", "NEG_EMOJI", "EMOJI", "EMOJI"]

# -------------------------
# 3. Url, hashtag, mention
# -------------------------
def test_url(tokenizer):
    tokens = tokenizer.tokenize("https://example.com http://test.com")
    assert tokens == ["URL", "URL"]

def test_hashtag(tokenizer):
    tokens = tokenizer.tokenize("#python #pytest")
    assert tokens == ["HASHTAG", "HASHTAG"]

def test_mention(tokenizer):
    tokens = tokenizer.tokenize("@user1 @user2")
    assert tokens == ["MENTION", "MENTION"]

# -------------------------
# 4. Mixed cases
# -------------------------
def test_mixed_text(tokenizer):
    text = "i stupid 😀 #fun @user https://test.com porn"
    tokens = tokenizer.tokenize(text)
    expected = ["PRONOUN_SELF", "BADWORD", "EMOJI", "HASHTAG", "MENTION", "URL", "SEXWORD"]
    assert tokens == expected

def test_mixed_text_with_numbers(tokenizer):
    text = "us buy now 1234 #deal @shop 😀"
    tokens = tokenizer.tokenize(text)
    expected = ["PRONOUN_GROUP", "SPAMWORD", "WORD", "HASHTAG", "MENTION", "EMOJI"]
    assert tokens == expected

def test_multiple_emojis(tokenizer):
    text = "😀😀😀😀😀😀"
    tokens = tokenizer.tokenize(text)
    expected = ["EMOJI"] * 6
    assert tokens == expected

def test_mixed_text_with_all_categories(tokenizer):
    text = "you porn kill 💀 https://x.com #warning @user"
    tokens = tokenizer.tokenize(text)
    expected = ["PRONOUN_OTHER", "SEXWORD", "VIOLENCE", "NEG_EMOJI", "URL", "HASHTAG", "MENTION"]
    assert tokens == expected

def test_mixed_text_with_adjacent_tokens(tokenizer):
    text = "hello😀buy now💀world"
    tokens = tokenizer.tokenize(text)
    expected = ["WORD", "EMOJI", "SPAMWORD", "NEG_EMOJI", "WORD"]
    assert tokens == expected

def test_mixed_text_with_fakeclaims_and_politics(tokenizer):
    text = "miracle cure democrats #vote @news"
    tokens = tokenizer.tokenize(text)
    expected = ["FAKECLAIM", "POLITIC", "HASHTAG", "MENTION"]
    assert tokens == expected

def test_mixed_text_only_symbols(tokenizer):
    text = "!@# $%^ &*()"
    tokens = tokenizer.tokenize(text)
    assert tokens == ["WORD", "WORD", "WORD"]

# -------------------------
# 5. Edge cases
# -------------------------
def test_unknown_symbols(tokenizer):
    tokens = tokenizer.tokenize("1234 !@#$")
    assert tokens == ["WORD", "WORD"]

def test_combined_emojis_and_words(tokenizer):
    tokens = tokenizer.tokenize("hello😀stupid💀")
    assert tokens == ["WORD", "EMOJI", "BADWORD", "NEG_EMOJI"]
