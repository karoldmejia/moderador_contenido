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
    html = transform_post("$\frac{x+1}{y-1}$")
    text = html["text"]

    assert "\frac{x + 1}{y - 1}" in text

def test_render_sqrt_no_index():
    html = transform_post("$\sqrt{9}$")
    text = html["text"]

    assert text == "$\sqrt{9}$"
    assert "9" in text

def test_render_sqrt_with_index():
    html = transform_post("$\sqrt[3]{x}$")
    text = html["text"]

    assert text == "$\sqrt[3]{x}$"
    assert "\sqrt[3]" in text
    assert "x" in text

def test_render_subsup():
    html = transform_post("$A^{2}+B^{2}=C^{2}$")
    text = html["text"]

    assert "A^{2}" in text
    assert "B^{2}" in text
    assert "C^{2}" in text

def test_render_group():
    html = transform_post("$(a+b)$")
    text = html["text"]

    assert "a + b" in text

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
    text = "The fraction is $\frac{x+1}{y-1}$ and the result is great"
    result = transform_post(text)
    html = result["text"]
    enh = result["enhancements"]

    assert "$\frac{x + 1}{y - 1}$" in html, "The fraction was not rendered"
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
    assert "$\\frac{x}{y}$" in html 

    # Invalid formula stays untouched
    assert "$(x+1//y)$" in html, "Invalid formula was not preserved as-is"