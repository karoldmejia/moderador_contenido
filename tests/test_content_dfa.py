import pytest
from src.content_dfa import ContentDFA

@pytest.fixture
def dfa():
    return ContentDFA()


def run_dfa_on_text(dfa, text):
    """
    Processes a complete text with the content DFA
    and returns the final state.
    """
    return dfa.process_text(text)


# -------------------------
# 1. Base cases without detection
# -------------------------

def test_empty_input(dfa):
    result = run_dfa_on_text(dfa, "")
    assert result == dfa.qF_Safe

def test_only_irrelevant_tokens(dfa):
    result = run_dfa_on_text(dfa, "I went to the park today")
    assert result == dfa.qF_Safe


# -------------------------
# 2. Badwords
# -------------------------

def test_badword_self(dfa):
    result = run_dfa_on_text(dfa, "I am such an idiot")
    assert result == dfa.qF_Offensive

def test_badword_generic(dfa):
    result = run_dfa_on_text(dfa, "This app is shit")
    assert result == dfa.qF_Hate

def test_badword_others(dfa):
    result = run_dfa_on_text(dfa, "You are a fucking idiot")
    assert result == dfa.qF_Hate


# -------------------------
# 3. Politics
# -------------------------

def test_politics_self(dfa):
    result = run_dfa_on_text(dfa, "I hate politicians")
    assert result == dfa.qF_Offensive

def test_politics_generic(dfa):
    result = run_dfa_on_text(dfa, "Politics is bullshit")
    assert result == dfa.qF_Hate

def test_politics_others(dfa):
    result = run_dfa_on_text(dfa, "Those politicians are corrupt assholes")
    assert result == dfa.qF_Hate


# -------------------------
# 4. Sexual
# -------------------------

def test_sexword_self(dfa):
    result = run_dfa_on_text(dfa, "I am horny af")
    assert result == dfa.qF_Sex

def test_sexword_generic(dfa):
    result = run_dfa_on_text(dfa, "This movie is so sexy")
    assert result == dfa.qF_Sex

def test_sexword_others(dfa):
    result = run_dfa_on_text(dfa, "I wanna grab your pussy")
    assert result == dfa.qF_Harass


# -------------------------
# 5. Violence
# -------------------------

def test_violence_self(dfa):
    result = run_dfa_on_text(dfa, "I want to kill myself")
    assert result == dfa.qF_SelfHarm

def test_violence_generic(dfa):
    result = run_dfa_on_text(dfa, "Violence is everywhere")
    assert result == dfa.qF_Safe

def test_violence_others(dfa):
    result = run_dfa_on_text(dfa, "I will kill you")
    assert result == dfa.qF_Threats


# -------------------------
# 6. Mixtures
# -------------------------

def test_multiple_tokens_irrelevant_then_badword(dfa):
    result = run_dfa_on_text(dfa, "Well you are such a dumb idiot")
    assert result == dfa.qF_Hate

def test_multiple_irrelevant_then_sexword(dfa):
    result = run_dfa_on_text(dfa, "This song is damn sexy")
    assert result == dfa.qF_Sex

def test_multiple_irrelevant_then_politics(dfa):
    result = run_dfa_on_text(dfa, "Honestly politics is shit")
    assert result == dfa.qF_Hate

def test_multiple_irrelevant_then_violence(dfa):
    result = run_dfa_on_text(dfa, "Sometimes I think about hurting others")
    assert result == dfa.qF_Threats

# -------------------------
# 7. Combinations politics + badwords
# -------------------------

def test_politics_then_badword_self(dfa):
    result = run_dfa_on_text(dfa, "These politicians are idiots")
    assert result == dfa.qF_Hate

def test_politics_then_badword_generic(dfa):
    result = run_dfa_on_text(dfa, "Politics is stupid shit")
    assert result == dfa.qF_Hate

def test_politics_then_badword_others(dfa):
    result = run_dfa_on_text(dfa, "Those politicians are fucking idiots")
    assert result == dfa.qF_Hate


def test_badword_then_politics_self(dfa):
    result = run_dfa_on_text(dfa, "Dumb politicians")
    assert result == dfa.qF_Hate

def test_badword_then_politics_generic(dfa):
    result = run_dfa_on_text(dfa, "Shitty politics")
    assert result == dfa.qF_Hate

def test_badword_then_politics_others(dfa):
    result = run_dfa_on_text(dfa, "Fucking politicians")
    assert result == dfa.qF_Hate


# -------------------------
# 8. Combinations politics + violence
# -------------------------

def test_politics_then_violence_self(dfa):
    result = run_dfa_on_text(dfa, "I want to attack politicians")
    assert result == dfa.qF_Violence

def test_politics_then_violence_generic(dfa):
    result = run_dfa_on_text(dfa, "Violence from politicians is everywhere")
    assert result == dfa.qF_Safe

def test_politics_then_violence_others(dfa):
    result = run_dfa_on_text(dfa, "We should kill corrupt politicians")
    assert result == dfa.qF_Hate

def test_violence_then_politics_self(dfa):
    result = run_dfa_on_text(dfa, "I will kill the politicians")
    assert result == dfa.qF_Violence

def test_violence_then_politics_generic(dfa):
    result = run_dfa_on_text(dfa, "Violence and politics always mix")
    assert result == dfa.qF_Safe

def test_violence_then_politics_others(dfa):
    result = run_dfa_on_text(dfa, "He wants to kill politicians")
    assert result == dfa.qF_Hate
