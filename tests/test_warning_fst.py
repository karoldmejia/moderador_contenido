import pytest
from src.warning_fst import WarningFST

@pytest.fixture
def fst():
    return WarningFST()

# ------------------------
# Tests individuales por estado
# ------------------------
def test_warning_spam(fst):
    assert fst.generate_warning("qSpam") == "this post may contain spam"

def test_warning_offensive(fst):
    assert fst.generate_warning("qF_Offensive") == "this post may contain offensive language"

def test_warning_hate(fst):
    assert fst.generate_warning("qF_Hate") == "this post may contain hate speech"

def test_warning_sex(fst):
    assert fst.generate_warning("qF_Sex") == "this post may contain sexual content"

def test_warning_harass(fst):
    assert fst.generate_warning("qF_Harass") == "this post may contain harassment"

def test_warning_selfharm(fst):
    assert fst.generate_warning("qF_SelfHarm") == "this post may contain self-harm"

def test_warning_threats(fst):
    assert fst.generate_warning("qF_Threats") == "this post may contain threats"

def test_warning_violence(fst):
    assert fst.generate_warning("qF_Violence") == "this post may contain violence"

# ------------------------
# Casos especiales
# ------------------------
def test_warning_safe_returns_none(fst):
    assert fst.generate_warning("qF_Safe") is None

def test_warning_unknown_state(fst):
    assert fst.generate_warning("qXYZ") is None

def test_warning_empty_string(fst):
    assert fst.generate_warning("") is None

def test_warning_none_input(fst):
    assert fst.generate_warning(None) is None

# ------------------------
# Secuencia de entradas
# ------------------------
def test_multiple_inputs_sequence(fst):
    results = [
        fst.generate_warning("qSpam"),
        fst.generate_warning("qF_Sex"),
        fst.generate_warning("qF_Safe"),
    ]
    assert results == [
        "this post may contain spam",
        "this post may contain sexual content",
        None,
    ]

# ------------------------
# Robustez
# ------------------------
def test_case_sensitivity(fst):
    # El FST espera nombres exactos, así que debe devolver None si no coincide
    assert fst.generate_warning("qspam") is None

def test_long_invalid_state(fst):
    long_state = "q" + "X" * 1000
    assert fst.generate_warning(long_state) is None
