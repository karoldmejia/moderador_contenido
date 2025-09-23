import pytest
from src.preprocessing import RegexTokenizer
from pathlib import Path

# ---------------------- FIXTURE ----------------------
@pytest.fixture
def tokenizer():
    """
    Provides a RegexTokenizer instance using the original keywords.json in src/data.
    """
    keywords_file = Path(__file__).parent.parent / "src" / "data" / "keywords.json"
    return RegexTokenizer(keywords_file=keywords_file)

# ---------------------- UNIT TESTS ----------------------

def test_badwords(tokenizer):
    tokens = tokenizer.tokenize("stupid")
    assert tokens == ["BADWORD"]

def test_sexwords(tokenizer):
    tokens = tokenizer.tokenize("porn")
    assert tokens == ["SEXWORD"]

def test_violence(tokenizer):
    tokens = tokenizer.tokenize("kill")
    assert tokens == ["VIOLENCE"]

def test_drugs(tokenizer):
    tokens = tokenizer.tokenize("cocaine")
    assert tokens == ["DRUG"]

def test_selfharm(tokenizer):
    tokens = tokenizer.tokenize("cut")
    assert tokens == ["SELFHARM"]

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
    assert tokens == ["PRONOUN", "PRONOUN"]

def test_normal_word(tokenizer):
    tokens = tokenizer.tokenize("hello world")
    assert tokens == ["WORD", "WORD"]

# ---------------------- EMOJIS ----------------------
def test_good_emoji(tokenizer):
    tokens = tokenizer.tokenize("😀 😃")
    assert tokens == ["EMOJI", "EMOJI"]

def test_bad_emoji(tokenizer):
    tokens = tokenizer.tokenize("💥 💀")
    assert tokens == ["NEG_EMOJI", "NEG_EMOJI"]

def test_mixed_emojis(tokenizer):
    tokens = tokenizer.tokenize("😀 💥 😃 💀")
    assert tokens == ["EMOJI", "NEG_EMOJI", "EMOJI", "NEG_EMOJI"]

# ---------------------- URL, HASHTAG, MENTION ----------------------
def test_url(tokenizer):
    tokens = tokenizer.tokenize("https://example.com http://test.com")
    assert tokens == ["URL", "URL"]

def test_hashtag(tokenizer):
    tokens = tokenizer.tokenize("#python #pytest")
    assert tokens == ["HASHTAG", "HASHTAG"]

def test_mention(tokenizer):
    tokens = tokenizer.tokenize("@user1 @user2")
    assert tokens == ["MENTION", "MENTION"]

# ---------------------- MIXED CASE ----------------------
def test_mixed_text(tokenizer):
    text = "i stupid 😀 #fun @user https://test.com porn"
    tokens = tokenizer.tokenize(text)
    expected = ["PRONOUN", "BADWORD", "EMOJI", "HASHTAG", "MENTION", "URL", "SEXWORD"]
    assert tokens == expected

def test_mixed_text_with_numbers(tokenizer):
    text = "i buy now 1234 #deal @shop 😀"
    tokens = tokenizer.tokenize(text)
    expected = ["PRONOUN", "SPAMWORD", "WORD", "HASHTAG", "MENTION", "EMOJI"]
    assert tokens == expected

def test_multiple_emojis(tokenizer):
    text = "😀😀😀😀😀😀"
    tokens = tokenizer.tokenize(text)
    expected = ["EMOJI", "EMOJI", "EMOJI", "EMOJI", "EMOJI", "EMOJI"]
    assert tokens == expected

def test_mixed_text_with_all_categories(tokenizer):
    text = "you cut cocaine porn kill 💀 https://x.com #warning @user"
    tokens = tokenizer.tokenize(text)
    expected = ["PRONOUN", "SELFHARM", "DRUG", "SEXWORD", "VIOLENCE", "NEG_EMOJI", "URL", "HASHTAG", "MENTION"]
    assert tokens == expected

def test_mixed_text_with_adjacent_tokens(tokenizer):
    text = "hello😀buy now💥world"
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
    # Each unrecognized symbol sequence is considered WORD
    assert tokens == ["WORD", "WORD", "WORD"]

# ---------------------- EDGE CASES ----------------------
def test_unknown_symbols(tokenizer):
    tokens = tokenizer.tokenize("1234 !@#$")
    # Numbers and unrecognized symbols are considered WORD
    assert tokens == ["WORD", "WORD"]

def test_combined_emojis_and_words(tokenizer):
    tokens = tokenizer.tokenize("hello😀stupid💥")
    # Each emoji detected separately
    assert tokens == ["WORD", "EMOJI", "BADWORD", "NEG_EMOJI"]
