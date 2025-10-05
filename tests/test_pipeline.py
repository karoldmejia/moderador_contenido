import pytest
from src.pipeline import TextPipeline

@pytest.fixture
def pipeline():
    return TextPipeline()

def test_safe_text(pipeline):
    text = "Hello everyone! Have a great day :)"
    result = pipeline.run(text)["final"]
    assert result["warnings"] == []

def test_badword_text(pipeline):
    text = "You are a stupid person"
    result = pipeline.run(text)["final"]
    assert "this post may contain hate speech" in result["warnings"]
    assert "stupid" not in result["text"].lower()

def test_sexword_text(pipeline):
    text = "He watched porn last night"
    result = pipeline.run(text)["final"]
    assert "this post may contain harassment" in result["warnings"]
    assert "porn" not in result["text"].lower()

def test_violence_text(pipeline):
    text = "I will kill him if he comes"
    result = pipeline.run(text)["final"]
    assert "this post may contain threats" in result["warnings"]
    assert "kill" not in result["text"].lower()

def test_spam_text(pipeline):
    text = "Check this out http://spam.com http://spam.com http://spam.com http://spam.com"
    result = pipeline.run(text)["final"]
    assert "this post may contain spam" in result["warnings"]

def test_hashtags_mentions(pipeline):
    text = "Hey @john, check out #Python #AI"
    result = pipeline.run(text)["final"]
    assert result["warnings"] == []

def test_formula_text(pipeline):
    text = "The fraction is $\frac{x+1}{y-1}$"
    result = pipeline.run(text)["final"]
    assert result["warnings"] == []
    assert "$\frac{x + 1}{y - 1}$" in result["text"]

def test_badword_sexword_text(pipeline):
    text = "You are a stupid idiot and watched porn"
    result = pipeline.run(text)["final"]
    assert "this post may contain hate speech" in result["warnings"]
    assert "stupid" not in result["text"].lower()
    assert "porn" not in result["text"].lower()

def test_pronouns_violence_text(pipeline):
    text = "They should die for this crime"
    result = pipeline.run(text)["final"]
    assert "this post may contain violence" in result["warnings"]
    assert "die" not in result["text"].lower()

def test_mixed_elements_text(pipeline):
    text = "Wow :) visit http://site.com #fun @alice you dumb"
    result = pipeline.run(text)["final"]
    assert "this post may contain hate speech" in result["warnings"]
    assert "dumb" not in result["text"].lower()
    assert "<a href=" in result["text"]  # link render
    assert "#fun" in result["text"]  # hashtag visible
    assert "@alice" in result["text"]  # mention visible
    assert "😊" in result["text"]  # emoji replaced
