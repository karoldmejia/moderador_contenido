import re
import pytest
from src.post_processor import enhance_post, render_formula, render_part, transform_post

# =======================================================
# TESTS FOR enhance_post
# =======================================================

def test_emoji_replacement():
    text = "Hello :-)"
    result = enhance_post(text)
    assert "😊" in result["text"]
    assert any("Emoji" in e for e in result["enhancements"])

def test_multiple_emojis():
    text = "Nice :D and sad :-("
    result = enhance_post(text)
    assert "😃" in result["text"] and "😢" in result["text"]

def test_link_detection():
    text = "Visit https://example.com for more info"
    result = enhance_post(text)
    assert "<a href='https://example.com'" in result["text"]
    assert "Link detected" in result["enhancements"]

def test_mention_detection():
    text = "Hi @karol!"
    result = enhance_post(text)
    assert "<span class='mention'>@karol</span>" in result["text"]
    assert "Mention detected" in result["enhancements"]

def test_hashtag_detection():
    text = "Loving the #sunset"
    result = enhance_post(text)
    assert "<span class='hashtag'>#sunset</span>" in result["text"]
    assert "Hashtag detected" in result["enhancements"]

def test_combined_features():
    text = "Hey @user check this link https://example.com #wow :-)"
    result = enhance_post(text)
    html = result["text"]
    assert "<span class='mention'>" in html
    assert "<a href=" in html
    assert "<span class='hashtag'>" in html
    assert "😊" in html

# =======================================================
# TESTS FOR render_formula
# =======================================================

def test_render_fraction():
    class Frac:
        def __init__(self):
            self.num = "x+1"
            self.den = "y-1"
    frac = Frac()
    html = render_formula(frac)
    assert "<span class='frac'>" in html
    assert "x+1" in html
    assert "y-1" in html


def test_render_sqrt_no_index():
    class Sqrt:
        def __init__(self):
            self.value = "9"
    sqrt = Sqrt()
    html = render_formula(sqrt)
    assert html == "√(9)"


def test_render_sqrt_with_index():
    class Sqrt:
        def __init__(self):
            self.value = "x"
            self.index = "3"
    sqrt = Sqrt()
    html = render_formula(sqrt)
    assert html == "√<sup>3</sup>(x)"


def test_render_subsup():
    class SubSup:
        def __init__(self):
            self.base = "x"
            self.sup = "2"
            self.sub = "i"
    subsup = SubSup()
    html = render_formula(subsup)
    assert "<sup>2</sup>" in html and "<sub>i</sub>" in html


def test_render_group():
    class Group:
    
        def __init__(self):
            self.expr = "a+b"
    group = Group()
    html = render_formula(group)
    assert html == "(a+b)"

# =======================================================
# TESTS FOR render_part
# =======================================================

def test_render_bold():
    class Bold:
        _tx_frozen_str = "*strong*"
    part = Bold()
    enhancements = []
    html = render_part(part, enhancements)
    assert html == "<b>strong</b>"
    assert "Bold formatting" in enhancements


def test_render_italic():
    class Italic:
        _tx_frozen_str = "-soft-"
    part = Italic()
    enhancements = []
    html = render_part(part, enhancements)
    assert html == "<i>soft</i>"
    assert "Italic formatting" in enhancements


def test_render_underline():
    class Underline:
        _tx_frozen_str = "_under_"
    part = Underline()
    enhancements = []
    html = render_part(part, enhancements)
    assert html == "<u>under</u>"
    assert "Underline formatting" in enhancements


def test_render_font_style():
    class Font:
        _tx_frozen_str = "/ fancy /"
    part = Font()
    enhancements = []
    html = render_part(part, enhancements)
    assert "font-family:cursive" in html
    assert "Font style" in enhancements

# =======================================================
# TESTS FOR transform_post (integration)
# =======================================================

def test_transform_post_with_emojis_mentions_hashtags_links():
    text = "Hello @karol :-) visit https://example.com #peace"
    result = transform_post(text)
    html = result["text"]
    enh = result["enhancements"]

    assert "<span class='mention'>@karol</span>" in html
    assert "😊" in html
    assert "<a href=" in html
    assert "<span class='hashtag'>#peace</span>" in html
    assert any("Link detected" in e for e in enh)
    assert any("Mention detected" in e for e in enh)

def test_transform_post_with_formula():
    text = "The fraction is $\\frac{x+1}{y-1}$ and the result is great"
    result = transform_post(text)
    html = result["text"]
    enh = result["enhancements"]

    assert "<span class='frac'>" in html, "The fraction was not rendered"
    assert "Formula rendering" in enh

def test_transform_post_with_invalid_formula():
    text = "Weird result: $(x++1)/(y--1)$ makes no sense"
    result = transform_post(text)
    html = result["text"]
    enh = result["enhancements"]

    # The text should remain as-is (no transformation)
    assert "$(x++1)/(y--1)$" in html, "Invalid formula text was not preserved as-is"

def test_transform_post_mixed_valid_and_invalid_formulas():
    text = "Valid: $\\frac{x}{y}$ but this one fails: $(x+1//y)$"
    result = transform_post(text)
    html = result["text"]
    enh = result["enhancements"]

    # Valid formula should render
    assert "<span class='frac'>" in html or "√" in html or "<sup>" in html, \
        "Valid formula was not rendered"

    # Invalid formula stays untouched
    assert "$(x+1//y)$" in html, "Invalid formula was not preserved as-is"