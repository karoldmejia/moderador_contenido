import pytest
from src.censorship_fst import CensorshipFST

@pytest.fixture
def fst():
    return CensorshipFST()

def test_empty_input(fst):
    assert fst.process_text("") == ""

def test_safe_text(fst):
    text = "The president will speak today"
    expected = "The president will speak today"
    assert fst.process_text(text) == expected

def test_badword_simple(fst):
    text = "You are a stupid person"
    expected = "You are a ****** person"
    assert fst.process_text(text) == expected

def test_sexword_simple(fst):
    text = "He watched porn last night"
    expected = "He watched **** last night"
    assert fst.process_text(text) == expected

def test_violence_simple(fst):
    text = "They will kill him"
    expected = "They will **** him"
    assert fst.process_text(text) == expected

def test_multiple_badwords(fst):
    text = "You are a dumb idiot!"
    expected = "You are a **** *****!"
    assert fst.process_text(text) == expected

def test_badword_start(fst):
    text = "Asshole came to the party"
    expected = "******* came to the party"
    assert fst.process_text(text) == expected

def test_sexword_middle(fst):
    text = "She likes boobs and sex"
    expected = "She likes ***** and ***"
    assert fst.process_text(text) == expected

def test_violence_and_badword(fst):
    text = "The jerk tried to shoot them"
    expected = "The **** tried to ***** them"
    assert fst.process_text(text) == expected

def test_politics_safe(fst):
    text = "Liberals and conservatives are debating"
    expected = "Liberals and conservatives are debating"
    assert fst.process_text(text) == expected

def test_badword_with_bademoji(fst):
    text = "You are a bastard 💀"
    expected = "You are a ******* 💀"
    assert fst.process_text(text) == expected

def test_sexword_and_badword(fst):
    text = "That idiot watched porn yesterday"
    expected = "That ***** watched **** yesterday"
    assert fst.process_text(text) == expected

def test_multiple_offensive_words(fst):
    text = "Dumb moron asshole"
    expected = "**** ***** *******"
    assert fst.process_text(text) == expected

def test_safe_and_offensive(fst):
    text = "My friend is a jerk"
    expected = "My friend is a ****"
    assert fst.process_text(text) == expected

def test_long_mixed_text(fst):
    text = "The stupid jerk tried to kill her while watching porn"
    expected = "The ****** **** tried to **** her while watching ****"
    assert fst.process_text(text) == expected
