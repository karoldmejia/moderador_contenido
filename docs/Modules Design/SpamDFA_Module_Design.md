# SpamDFA — Module Design Document
**File:** `spam_dfa.py`  
**Date:** 2025-10-03  
**Language:** Python 3.8+  
**Status:** Stable

---

## 1. Abstract
`SpamDFA` classifies a text as **Spam** or **Safe** using a deterministic finite-state machine over a token stream produced by `RegexTokenizer`. The DFA increments **URL** and **HASHTAG** buckets via state transitions and immediately flags spam when a **spam phrase** marker is observed (`SPAMWORD` or `FAKECLAIM`). The decision is returned at end-of-input as either `qSpam` or `qSafe`.

---

## 2. Scope and Non‑Goals
**In scope**
- Count URLs and hashtags up to a fixed threshold (4th occurrence triggers spam).
- Immediate spam detection for phrase markers (`SPAMWORD`, `FAKECLAIM`).
- Deterministic classification with explicit states and transitions.

**Out of scope**
- Probabilistic scoring, templates, or ML models.
- Aggregating heterogeneous weak signals (e.g., 2 URLs + 2 hashtags) into spam.
- URL/domain reputation, link de-duplication, or time-windowed rate control.
- Language-specific heuristics and rich NLP features.

---

## 3. Glossary
- **Token**: Symbolic unit emitted by `RegexTokenizer` (e.g., `URL`, `HASHTAG`, `SPAMWORD`, `FAKECLAIM`, or Σ for others).
- **Σ (Sigma)**: Any token that is not `URL`, `HASHTAG`, `SPAMWORD`, or `FAKECLAIM`; Σ does not change the DFA’s spam counters.
- **Spam phrase markers**: Canonical placeholders inserted by preprocessing when multi‑word spam or false-claim phrases are matched: `SPAMWORD`, `FAKECLAIM`.

---

## 4. External Dependencies and Artifacts
- **Standard library**: `pathlib.Path`
- **Internal**: `preprocessing.RegexTokenizer` (consumes `data/keywords.json` to emit tokens).
- **Data file**: `data/keywords.json` (path resolved relative to the module).

`SpamDFA` assumes the tokenizer recognizes URLs, hashtags, and spam phrases and emits the corresponding tokens in lowercase/uppercase agnostic form (the DFA lowercases on input).

---

## 5. Public API
### 5.1 Class: `SpamDFA`
**Intent:** Binary spam detection over a token stream (Spam vs Safe).

**Constructor**
```python
SpamDFA()
```
- Binds a `RegexTokenizer` to the module’s `data/keywords.json`.
- Initializes states and sets current state to `q0`.

**Primary Method (Main Function)**
```python
process_text(self, text: str) -> str
```
- **Role:** End‑to‑end classification. Resets state, tokenizes the input, feeds tokens through `transition`, and returns the terminal via `end_of_input`.
- **Input:** Arbitrary Unicode string.
- **Output:** `"qSpam"` or `"qSafe"`.
- **Complexity:** O(n) in tokens, O(1) auxiliary space.

**Auxiliary Methods**
```python
reset(self) -> None
```
- Sets `state = q0`.

```python
transition(self, token: str) -> None
```
- Lowercases the token and updates the state according to the transition rules in §7.

```python
end_of_input(self) -> str
```
- Returns `qSpam` if the DFA is currently in `qSpam`; otherwise `qSafe`.

---

## 6. States
### 6.1 Intermediate States
| State | Meaning |
|---|---|
| `q0`  | Start / no counts yet |
| `qU1` | Saw 1 URL |
| `qU2` | Saw 2 URLs |
| `qU3` | Saw 3 URLs |
| `qH1` | Saw 1 Hashtag |
| `qH2` | Saw 2 Hashtags |
| `qH3` | Saw 3 Hashtags |

### 6.2 Terminal States
| State | Meaning |
|---|---|
| `qSpam` | Spam detected (final) |
| `qSafe` | Safe (final, returned when not in `qSpam`) |

---

## 7. Transition System
Only four token classes influence the DFA: `url`, `hashtag`, `spamword`, `fakeclaim`. All other tokens belong to Σ and do not change the state.

### 7.1 Transition Rules (pseudocode)
```text
# Start
q0  --spamword/fakeclaim--> qSpam
q0  --url---------------> qU1
q0  --hashtag-----------> qH1
q0  --Σ-----------------> q0

# URL counters
qU1 --url---------------> qU2
qU1 --spamword/fakeclaim--> qSpam
qU1 --Σ/hashtag---------> qU1   (sticky)

qU2 --url---------------> qU3
qU2 --spamword/fakeclaim--> qSpam
qU2 --Σ/hashtag---------> qU2   (sticky)

qU3 --url---------------> qSpam  (4th URL)
qU3 --spamword/fakeclaim--> qSpam
qU3 --Σ/hashtag---------> qU3   (sticky)

# Hashtag counters
qH1 --hashtag-----------> qH2
qH1 --spamword/fakeclaim--> qSpam
qH1 --Σ/url-------------> qH1   (sticky)

qH2 --hashtag-----------> qH3
qH2 --spamword/fakeclaim--> qSpam
qH2 --Σ/url-------------> qH2   (sticky)

qH3 --hashtag-----------> qSpam  (4th hashtag)
qH3 --spamword/fakeclaim--> qSpam
qH3 --Σ/url-------------> qH3   (sticky)

# Spam is absorbing
qSpam --(any)-----------> qSpam
```

### 7.2 Threshold Summary
- **URLs**: The **4th** `URL` token triggers `qSpam` (via `qU3 --url--> qSpam`).  
- **Hashtags**: The **4th** `HASHTAG` triggers `qSpam` (via `qH3 --hashtag--> qSpam`).  
- **Spam phrases**: Any `SPAMWORD` or `FAKECLAIM` triggers `qSpam` immediately from any non‑terminal state.

> **Note:** URL and hashtag counters are tracked **independently**; they do not add across categories. For example, 2 URLs + 2 hashtags → `qSafe` at end-of-input (see §11).

---

## 8. Combination and Finalization
`end_of_input()` returns:
- `qSpam` if the absorbing spam state has been reached during scanning.
- `qSafe` otherwise (including `qU1`, `qU2`, `qU3`, `qH1`, `qH2`, `qH3`, or `q0`).

This ensures a definitive binary result for any input.

---

## 9. Auxiliary Responsibilities (Conceptual Helpers)
Although not extracted in code, the following responsibilities can be factored into private helpers to improve readability and testability:

1. **Normalization**
   ```python
   _normalize(token: str) -> str
   # Lowercase/canonicalize tokens.
   ```

2. **URL Counter Update**
   ```python
   _update_url_state(current: str, token: str) -> str
   # Maps q0/qU1/qU2/qU3 + 'url' to the next state, else returns current.
   ```

3. **Hashtag Counter Update**
   ```python
   _update_hashtag_state(current: str, token: str) -> str
   # Maps q0/qH1/qH2/qH3 + 'hashtag' to the next state, else returns current.
   ```

4. **Spam Phrase Check**
   ```python
   _is_spam_phrase(token: str) -> bool
   # True if token ∈ {'spamword','fakeclaim'}.
   ```

5. **Absorbing State**
   ```python
   _absorb_spam(current: str) -> str
   # If current == qSpam, keep qSpam.
   ```

---

## 11. Correctness and Design Rationale
- **Monotonicity:** URL/hashtag counters never decrement; `qSpam` is absorbing. Once spam is detected, the outcome cannot revert.
- **Immediate phrase spam:** Phrase markers short‑circuit counting; this captures classic spam/false‑claim slogans without relying on volume.
- **Independence of counters:** URLs and hashtags are counted on **separate tracks**, which simplifies reasoning and bounds state space. This is intentional; “sum‑of‑signals” logic is out of scope.
- **Deterministic thresholds:** Using fixed cutoffs (4th occurrence) provides explainability and predictable behavior under testing and audits.

---

## 12. Interfaces and Contracts
### Inputs
- `text: str` — raw text to classify (the tokenizer handles tokenization).

### Outputs
- `"qSpam"` or `"qSafe"` (strings).

### Error Handling
- Construction can fail indirectly if `RegexTokenizer` cannot read or parse `keywords.json` (e.g., `FileNotFoundError`, `JSONDecodeError`).
- The DFA itself does not raise on normal inputs.

### Side Effects
- None beyond reading the keywords file at construction via the tokenizer.

### Thread Safety
- The instance keeps a mutable `state`; use one instance per thread/task or guard externally.

---

## 13. Test Plan
### 13.1 Unit Tests (pytest)
| ID | Scenario | Input | Expected |
|---|---|---|---|
| T1 | Empty text | `""` | `qSafe` |
| T2 | One URL | `"https://a.b"` | `qSafe` |
| T3 | Three URLs | `"a b https://1 https://2 https://3"` | `qSafe` |
| T4 | Four URLs | `"https://1 https://2 https://3 https://4"` | `qSpam` |
| T5 | One hashtag | `"#a"` | `qSafe` |
| T6 | Three hashtags | `"#a #b #c"` | `qSafe` |
| T7 | Four hashtags | `"#a #b #c #d"` | `qSpam` |
| T8 | Spam phrase | `"free money now"` | `qSpam` (via `SPAMWORD`) |
| T9 | Fake claim phrase | `"cure cancer fast"` | `qSpam` (via `FAKECLAIM`) |
| T10 | Mixed below thresholds | `"https://1 #a https://2 #b"` | `qSafe` |
| T11 | Absorbing spam | `"SPAMWORD then more"` | `qSpam` |
| T12 | Case‑insensitive tokens | `"FaKeClAiM"` | `qSpam` (lowercased) |

*Implementation detail:* For deterministic tests, mock `RegexTokenizer` to emit desired tokens or feed token strings directly through `transition()` and then call `end_of_input()`.

### 13.2 Property‑Based Checks (optional)
- **Monotonicity:** Appending Σ tokens to a spam‑classified sequence keeps the result `qSpam`.
- **Order invariance for counts:** Shuffling Σ tokens among URLs/hashtags does not change the final result as long as counts are preserved.

---

## 14. Appendix: Transition Tables
### 14.1 Content Transition Table
| From \ Token | `url` | `hashtag` | `spamword`/`fakeclaim` | Σ |
|---|---:|---:|---:|---:|
| `q0`  | `qU1` | `qH1` | `qSpam` | `q0` |
| `qU1` | `qU2` | `qU1` | `qSpam` | `qU1` |
| `qU2` | `qU3` | `qU2` | `qSpam` | `qU2` |
| `qU3` | `qSpam` | `qU3` | `qSpam` | `qU3` |
| `qH1` | `qH1` | `qH2` | `qSpam` | `qH1` |
| `qH2` | `qH2` | `qH3` | `qSpam` | `qH2` |
| `qH3` | `qH3` | `qSpam` | `qSpam` | `qH3` |
| `qSpam` | `qSpam` | `qSpam` | `qSpam` | `qSpam` |

### 14.2 Finalization
| State at `$` | Returned |
|---|---|
| `qSpam` | `qSpam` |
| `q0`, `qU1`, `qU2`, `qU3`, `qH1`, `qH2`, `qH3` | `qSafe` |
