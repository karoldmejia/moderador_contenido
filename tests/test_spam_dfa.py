import pytest
from src.spam_dfa import SpamDFA

@pytest.fixture
def dfa():
    return SpamDFA()

# -------------------------
# Safe cases
# -------------------------
def test_empty_input(dfa):
    assert dfa.process_text("") == dfa.qSafe

def test_safe_text_single_url(dfa):
    text = "Check out my blog at http://example.com"
    assert dfa.process_text(text) == dfa.qSafe

def test_safe_two_urls(dfa):
    text = "Visit http://site1.com and http://site2.com for details"
    assert dfa.process_text(text) == dfa.qSafe

def test_safe_three_hashtags(dfa):
    text = "#fun #coding #python"
    assert dfa.process_text(text) == dfa.qSafe

def test_safe_mixed_urls_and_hashtags(dfa):
    text = "http://abc.com #learn #code http://xyz.com"
    assert dfa.process_text(text) == dfa.qSafe

# -------------------------
# Direct spam cases
# -------------------------
def test_spamword_click_here(dfa):
    text = "Click here to win a free iPhone!"
    assert dfa.process_text(text) == dfa.qSpam

def test_spamword_buy_now(dfa):
    text = "Buy now, limited time offer!"
    assert dfa.process_text(text) == dfa.qSpam

def test_fakeclaim_guaranteed(dfa):
    text = "This miracle cure is 100% proven and guaranteed"
    assert dfa.process_text(text) == dfa.qSpam

def test_four_urls_spam(dfa):
    text = "http://a.com http://b.com http://c.com http://d.com"
    assert dfa.process_text(text) == dfa.qSpam

def test_four_hashtags_spam(dfa):
    text = "#promo #sale #discount #cheap"
    assert dfa.process_text(text) == dfa.qSpam

# -------------------------
# Mixed cases with spam
# -------------------------
def test_url_then_spamword(dfa):
    text = "Check this out http://abc.com and click here for details"
    assert dfa.process_text(text) == dfa.qSpam

def test_hashtag_then_fakeclaim(dfa):
    text = "#health miracle cure revealed today"
    assert dfa.process_text(text) == dfa.qSpam

def test_three_urls_then_fakeclaim(dfa):
    text = "http://a.com http://b.com http://c.com unbelievable secret formula"
    assert dfa.process_text(text) == dfa.qSpam

def test_two_hashtags_then_spamword(dfa):
    text = "#deal #promo get rich quick!"
    assert dfa.process_text(text) == dfa.qSpam

def test_mixed_safe_vs_spam(dfa):
    text = "http://abc.com #fun #coding http://xyz.com free money waiting"
    assert dfa.process_text(text) == dfa.qSpam
