from pyparsing import Path
import pytest
from src.directionality_dfa import DirectionalityDFA
from src.preprocessing import RegexTokenizer

@pytest.fixture(scope="module")
def tokenizer():
    keywords_path = Path(__file__).parent.parent / "src" / "data" / "keywords.json"
    return RegexTokenizer(str(keywords_path))

@pytest.fixture
def dfa():
    return DirectionalityDFA()


def run_analysis(text, tokenizer, dfa):
    tokens = tokenizer.tokenize(text)
    dfa.reset()
    for token in tokens:
        dfa.transition(token)
    final_state = dfa.end_of_input()
    return final_state, tokens


@pytest.mark.parametrize("text,expected_final", [
    ("I hate myself", "qF_Self"),         # self pronoun
    ("You are stupid", "qF_Others"),      # other pronoun
    ("This is terrible", "qF_Generic"),   # no pronoun
    ("We are better than you", "qF_Others"), # mixed: detects 'you'
    ("Nobody loves me", "qF_Self"),       # detects 'me'
    ("Life sucks", "qF_Generic")          # no pronoun
])
def test_directionality_with_real_phrases(tokenizer, dfa, text, expected_final):
    final_state, tokens = run_analysis(text, tokenizer, dfa)
    print(f"Text: {text} -> Tokens: {tokens} -> Final: {final_state}")
    assert final_state == expected_final
