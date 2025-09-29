import pytest
from pathlib import Path
from src.preprocessing import RegexTokenizer
from src.content_dfa import ContentDFA

@pytest.fixture(scope="module")
def dfa():
    return ContentDFA(keywords_file=Path(__file__).parent.parent / "src/data/keywords.json")


# -------------------------
# 1. Base cases without detection
# -------------------------

def test_empty_text(dfa):
    assert dfa.process_text("") == dfa.qF_Safe

def test_only_irrelevant_words(dfa):
    text = "Just chilling at home doing nothing"
    assert dfa.process_text(text) == dfa.qF_Safe

def test_irrelevant_then_generic_pronoun(dfa):
    text = "I love my cat"
    assert dfa.process_text(text) == dfa.qF_Safe  # no badwords, generic pronoun

# -------------------------
# 2. Badwords + directionality
# -------------------------

def test_badword_self(dfa):
    text = "I am an idiot"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_badword_others(dfa):
    text = "You are an idiot"
    assert dfa.process_text(text) == dfa.qF_Hate

def test_badword_generic(dfa):
    text = "This place is stupid"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_badword_with_irrelevant(dfa):
    text = "Wow, this is so bad you idiot"
    assert dfa.process_text(text) == dfa.qF_Hate

# -------------------------
# 3. Politics + directionality
# -------------------------

def test_politics_self(dfa):
    text = "I think the government is corrupt"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_politics_others(dfa):
    text = "They are corrupt politicians"
    assert dfa.process_text(text) == dfa.qF_Hate

def test_politics_generic(dfa):
    text = "Politics these days are ridiculous"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_politics_with_irrelevant(dfa):
    text = "Honestly, politics is boring but I voted"
    assert dfa.process_text(text) == dfa.qF_Offensive

# -------------------------
# 4. Sexual content + directionality
# -------------------------

def test_sexword_self(dfa):
    text = "I am feeling horny"
    assert dfa.process_text(text) == dfa.qF_Sex

def test_sexword_others(dfa):
    text = "You look sexy"
    assert dfa.process_text(text) == dfa.qF_Harass

def test_sexword_generic(dfa):
    text = "That scene was sexual"
    assert dfa.process_text(text) == dfa.qF_Sex

def test_sexword_with_irrelevant(dfa):
    text = "Hey, that girl is sexy"
    assert dfa.process_text(text) == dfa.qF_Harass

# -------------------------
# 5. Violence + directionality
# -------------------------

def test_violence_self(dfa):
    text = "I will hurt myself"
    assert dfa.process_text(text) == dfa.qF_SelfHarm

def test_violence_others(dfa):
    text = "I will attack you"
    assert dfa.process_text(text) == dfa.qF_Threats

def test_violence_generic(dfa):
    text = "Violence is everywhere"
    assert dfa.process_text(text) == dfa.qF_Violence

def test_violence_with_irrelevant(dfa):
    text = "Wow, so much violence lately"
    assert dfa.process_text(text) == dfa.qF_Violence

# -------------------------
# 6. Realistic mixed sequences
# -------------------------

def test_mixed_badword_then_sexword(dfa):
    text = "You idiot, stop being sexy"
    assert dfa.process_text(text) == dfa.qF_Hate

def test_irrelevant_then_badword(dfa):
    text = "Just chilling but stupid"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_irrelevant_then_sexword(dfa):
    text = "Walking around feeling horny"
    assert dfa.process_text(text) == dfa.qF_Sex

def test_irrelevant_then_politics(dfa):
    text = "Some thoughts about politics today"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_irrelevant_then_violence(dfa):
    text = "Just chilling seeing violence on TV"
    assert dfa.process_text(text) == dfa.qF_Violence

def test_multiple_tokens_with_badword(dfa):
    text = "Wow this stupid thing happened"
    assert dfa.process_text(text) == dfa.qF_Offensive

def test_multiple_tokens_with_sexword(dfa):
    text = "That sexy dress though"
    assert dfa.process_text(text) == dfa.qF_Harass

def test_multiple_tokens_with_politics(dfa):
    text = "Government politics is crazy"
    assert dfa.process_text(text) == dfa.qF_Hate

def test_multiple_tokens_with_violence(dfa):
    text = "Violence is everywhere nowadays"
    assert dfa.process_text(text) == dfa.qF_Safe

def test_only_irrelevant_and_pronoun(dfa):
    text = "I love my dog"
    assert dfa.process_text(text) == dfa.qF_Safe
