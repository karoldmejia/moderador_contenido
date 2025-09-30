import pytest
from pathlib import Path
from src.preprocessing import RegexTokenizer
from src.content_dfa import ContentDFA


@pytest.fixture(scope="module")
def tokenizer():
    keywords_path = Path(__file__).parent.parent / "src" / "data" / "keywords.json"
    return RegexTokenizer(str(keywords_path))


@pytest.fixture
def dfa():
    return ContentDFA()


def run_dfa_on_text(dfa, tokenizer, text, direction_final):
    """
    Tokeniza el texto, pasa cada token por el DFA,
    y retorna el estado final.
    """
    dfa.reset()
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        dfa.transition(token)
    return dfa.end_of_input(direction_final)


# -------------------------
# 1. Base cases without detection
# -------------------------

def test_empty_input(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "", "qF_Generic")
    assert result == dfa.qF_Safe

def test_only_irrelevant_tokens(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I went to the park today", "qF_Generic")
    assert result == dfa.qF_Safe


# -------------------------
# 2. Badwords
# -------------------------

def test_badword_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I am such an idiot", "qF_Self")
    assert result == dfa.qF_Offensive

def test_badword_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "This app is shit", "qF_Generic")
    assert result == dfa.qF_Offensive

def test_badword_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "You are a fucking idiot", "qF_Others")
    assert result == dfa.qF_Hate


# -------------------------
# 3. Politics
# -------------------------

def test_politics_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I hate politicians", "qF_Self")
    assert result == dfa.qF_Offensive

def test_politics_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Politics is bullshit", "qF_Generic")
    assert result == dfa.qF_Offensive

def test_politics_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Those politicians are corrupt assholes", "qF_Others")
    assert result == dfa.qF_Hate


# -------------------------
# 4. Sexual
# -------------------------

def test_sexword_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I am horny af", "qF_Self")
    assert result == dfa.qF_Sex

def test_sexword_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "This movie is so sexy", "qF_Generic")
    assert result == dfa.qF_Sex

def test_sexword_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I wanna grab your pussy", "qF_Others")
    assert result == dfa.qF_Harass


# -------------------------
# 5. Violence
# -------------------------

def test_violence_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I want to kill myself", "qF_Self")
    assert result == dfa.qF_SelfHarm

def test_violence_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Violence is everywhere", "qF_Generic")
    assert result == dfa.qF_Safe

def test_violence_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I will kill you", "qF_Others")
    assert result == dfa.qF_Threats


# -------------------------
# 6. Mixtures
# -------------------------

def test_multiple_tokens_irrelevant_then_badword(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Well you are such a dumb idiot", "qF_Others")
    assert result == dfa.qF_Hate

def test_multiple_irrelevant_then_sexword(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "This song is damn sexy", "qF_Generic")
    assert result == dfa.qF_Sex

def test_multiple_irrelevant_then_politics(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Honestly politics is shit", "qF_Generic")
    assert result == dfa.qF_Offensive

def test_multiple_irrelevant_then_violence(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Sometimes I think about hurting others", "qF_Others")
    assert result == dfa.qF_Threats

# -------------------------
# 7. Combinations Politics + Badwords
# -------------------------

def test_politics_then_badword_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "These politicians are idiots", "qF_Self")
    assert result == dfa.qF_Offensive

def test_politics_then_badword_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Politics is stupid shit", "qF_Generic")
    assert result == dfa.qF_Offensive

def test_politics_then_badword_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Those politicians are fucking idiots", "qF_Others")
    assert result == dfa.qF_Hate


def test_badword_then_politics_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Dumb politicians", "qF_Self")
    assert result == dfa.qF_Offensive

def test_badword_then_politics_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Shitty politics", "qF_Generic")
    assert result == dfa.qF_Offensive

def test_badword_then_politics_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Fucking politicians", "qF_Others")
    assert result == dfa.qF_Hate


# -------------------------
# 8. Combinations Politics + Violence
# -------------------------

def test_politics_then_violence_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I want to attack politicians", "qF_Self")
    assert result == dfa.qF_Violence

def test_politics_then_violence_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Violence from politicians is everywhere", "qF_Generic")
    assert result == dfa.qF_Safe

def test_politics_then_violence_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "We should kill corrupt politicians", "qF_Others")
    assert result == dfa.qF_Hate

def test_violence_then_politics_self(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "I will kill the politicians", "qF_Self")
    assert result == dfa.qF_Violence

def test_violence_then_politics_generic(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "Violence and politics always mix", "qF_Generic")
    assert result == dfa.qF_Safe

def test_violence_then_politics_others(dfa, tokenizer):
    result = run_dfa_on_text(dfa, tokenizer, "He wants to kill politicians", "qF_Others")
    assert result == dfa.qF_Hate
