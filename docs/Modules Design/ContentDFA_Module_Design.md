# ContentDFA — Module Design Document
**File:** `content_dfa.py`  
**Date:** 2025‑10‑03  
**Language:** Python 3.8+  
**Status:** Stable

---

## 1. Abstract
This module implements a deterministic finite‑state machine (DFA) to categorize text based on **content triggers** (badwords, politics, sex, violence) and **directionality** (self, others, generic). Tokens are produced by a preprocessing component and consumed by two cooperating DFAs:
- **ContentDFA** (this module): tracks semantic triggers and combinations across the token stream.
- **DirectionalityDFA**: tracks who the text is about (self vs others vs generic).

At end of input, both DFAs are finalized and their outcomes are **combined** into a single **final label** (e.g., `qF_Hate`, `qF_SelfHarm`, `qF_Sex`, `qF_Safe`). The design emphasizes clear state semantics, predictable transitions, and explicit category combination logic.

---

## 2. Scope and Non‑Goals
**In scope**
- Classifying text into final categories using discrete token classes: `BADWORD`, `POLITIC`, `SEXWORD`, `VIOLENCE`, plus Σ (all other tokens).
- Tracking hybrid content states (`qPB`, `qPV`) to capture interactions between politics and badwords/violence.
- Delegating person‑reference analysis to `DirectionalityDFA` and combining both results deterministically.

**Out of scope**
- Tokenization rules and keyword maintenance (handled by `RegexTokenizer` and its `keywords.json`).
- Fuzzy matching, semantic embeddings, or phrase‑level inference.
- Scoring or calibration; this DFA outputs a single categorical state.
- Streaming I/O; callers provide a complete string and receive a categorical result.

---

## 3. Glossary
- **Token**: A symbolic label emitted by preprocessing, e.g., `BADWORD`, `POLITIC`, `SEXWORD`, `VIOLENCE`, or any other Σ token.
- **Σ (Sigma)**: The set of all tokens not explicitly handled as triggers; Σ tokens do not change content state.
- **Directionality**: Target of the message—`Self`, `Others`, or `Generic`—determined by `DirectionalityDFA` (e.g., first‑person vs second/third‑person references).
- **Final label**: A terminal category returned after end‑of‑input by combining content and directionality states.

---

## 4. External Dependencies and Artifacts
- **Standard library**: `pathlib.Path`
- **Internal modules**:
  - `preprocessing.RegexTokenizer`: builds tokens from raw text using a JSON keyword file.
  - `directionality_dfa.DirectionalityDFA`: independent DFA that classifies directionality over the same token stream.
- **Data file**: `data/keywords.json` (paths passed to `RegexTokenizer`). A typical schema is:
  ```json
  {
    "badwords":  ["..."],
    "sexwords":  ["..."],
    "violence":  ["..."],
    "politics":  ["..."],
    "pronouns":  { "self": ["I","me","my", ...], "others": ["you","they", ...] }
  }
  ```
  Exact fields are defined by the tokenizer; ContentDFA only consumes the resulting tokens.

---

## 5. Public API
### 5.1 Class: `ContentDFA`
**Intent:** Track content triggers and return a final category after combining with directionality.

**Constructor**
```python
ContentDFA()
```
- Creates a `RegexTokenizer` bound to the module’s `data/keywords.json`.
- Instantiates a `DirectionalityDFA`.
- Initializes content states and sets current state to `q0`.

**Primary Method (Main Function)**
```python
process_text(self, text: str) -> str
```
- **Role:** End‑to‑end classification over a complete text. Resets both DFAs, tokenizes input, feeds each token into both DFAs, and returns the combined final label.
- **Input:** `text` — arbitrary Unicode string.
- **Output:** One of the final content labels:
  - `qF_Offensive`, `qF_Hate`, `qF_Sex`, `qF_Harass`, `qF_SelfHarm`, `qF_Threats`, `qF_Violence`, `qF_Safe`.
- **Determinism:** Same input and keyword sets yield the same final label.
- **Complexity:** O(n) in number of tokens, O(1) additional space.

**Auxiliary Methods**
```python
reset(self) -> None
```
- Resets content state to `q0` and resets `DirectionalityDFA`.

```python
transition(self, token: str) -> None
```
- Advances content state using a single token (uppercased internally), following the transition table in §7.

```python
end_of_input(self) -> str | None
```
- Finalizes directionality DFA and maps the pair `(content_state, directionality_final)` to a single terminal label.

---

## 6. Content States and Final Labels
### 6.1 Intermediate Content States (non‑final)
| State | Meaning |
|---|---|
| `q0`  | Start / no triggers observed |
| `qB`  | Badword present |
| `qP`  | Politics present |
| `qPB` | Politics + Badword observed (order‑agnostic) |
| `qV`  | Violence present |
| `qPV` | Politics + Violence observed (order‑agnostic) |
| `qS`  | Sexword present |

### 6.2 Final Labels (terminals)
| Final | Meaning |
|---|---|
| `qF_Offensive` | Offensive language directed at **self** (incl. badwords without external target) |
| `qF_Hate`      | Abusive/hostile content directed at **others** or **generic groups**, incl. political contextualization (`qPB`, `qPV`) where applicable |
| `qF_Sex`       | Sexual content without a targeted harassing direction (self/generic) |
| `qF_Harass`    | Sexual content aimed at **others** |
| `qF_SelfHarm`  | Violence directed at **self** |
| `qF_Threats`   | Violence directed at **others** (threats) |
| `qF_Violence`  | Generic or contextual violence without a specific person target |
| `qF_Safe`      | No content triggers |

**Directionality terminals** (produced by `DirectionalityDFA`):
- `qF_Self`, `qF_Others`, `qF_Generic`

---

## 7. Transition System (ContentDFA)
Content state is updated token‑by‑token using only the four trigger classes; all other tokens are Σ and do not alter the state.

### 7.1 Transition Rules (pseudocode)
```text
q0  --BADWORD--> qB          q0  --POLITIC--> qP        q0 --SEXWORD--> qS        q0 --VIOLENCE--> qV
qB  --POLITIC--> qPB         qB  --(BADWORD|Σ)--> qB
qP  --BADWORD--> qPB         qP  --VIOLENCE--> qPV      qP --(POLITIC|Σ)--> qP
qV  --POLITIC--> qPV         qV  --(VIOLENCE|Σ)--> qV
qS  --(SEXWORD|Σ)--> qS
qPB --(BADWORD|POLITIC|Σ)--> qPB
qPV --(VIOLENCE|POLITIC|Σ)--> qPV
```

### 7.2 Implementation Notes
- Tokens are uppercased before comparison, ensuring consistent matching against trigger names.
- Order is not relevant for hybrid states: `qP`→`BADWORD` and `qB`→`POLITIC` both land in `qPB`; same for `qPV`.
- Σ includes any token class not listed above; Σ is a no‑op for content state.

---

## 8. Combination Logic at End‑of‑Input
After consuming all tokens, `end_of_input` retrieves `direction_final = DirectionalityDFA.end_of_input()` and maps `(content_state, direction_final)` to a terminal:

- **Badword only (`qB`)**  
  - `qF_Self`    → `qF_Offensive`  
  - `qF_Others` or `qF_Generic` → `qF_Hate`

- **Politics only (`qP`)**  
  - Always → `qF_Safe`

- **Politics + Badword (`qPB`)**  
  - `qF_Self`    → `qF_Offensive`  
  - `qF_Others` or `qF_Generic` → `qF_Hate`

- **Sexword only (`qS`)**  
  - `qF_Self` or `qF_Generic` → `qF_Sex`  
  - `qF_Others` → `qF_Harass`

- **Violence only (`qV`)**  
  - `qF_Self`    → `qF_SelfHarm`  
  - `qF_Others`  → `qF_Threats`  
  - `qF_Generic` → `qF_Violence`

- **Politics + Violence (`qPV`)**  
  - `qF_Generic` or `qF_Others` → `qF_Hate`  
  - `qF_Self`                   → `qF_Violence`

- **No triggers (`q0`)** → `qF_Safe`  
- **Otherwise** → `None` (no terminal found; indicates misconfiguration or unexpected state)

---

## 9. Algorithm and Control Flow
```text
process_text(text):
  reset content + directionality
  tokens = RegexTokenizer(keywords.json).tokenize(text)
  for tok in tokens:
    directionality.transition(tok)   # updates person-target signals
    content.transition(tok)          # updates content triggers/hybrids
  return end_of_input()              # combine both outcomes into a final label
``

---

## 10. Auxiliary Responsibilities (Conceptual Helpers)
Although implemented inline, the following responsibilities are logically separate and can be factored into private helpers for clarity and testability:

1. **Token Normalization**
   ```python
   _normalize(token: str) -> str
   # Uppercase and trim; returns canonical trigger name or original token.
   ```

2. **Content Transition Predicate**
   ```python
   _is_trigger(token: str) -> bool
   # True if token ∈ {BADWORD, POLITIC, SEXWORD, VIOLENCE}.
   ```

3. **Hybrid State Promotion**
   ```python
   _promote_hybrid(current: str, token: str) -> str
   # Returns qPB or qPV where appropriate, otherwise current.
   ```

4. **Final Mapping**
   ```python
   _combine(content_state: str, direction_final: str) -> str | None
   # Implements §8 mapping; the single source of truth for terminals.
   ```

Extracting these helpers enables granular unit tests, simplifies maintenance, and constrains behavior to a single mapping table.

---

## 10. Interfaces and Contracts
### Inputs
- `text: str` — arbitrary Unicode; may be empty.

### Outputs
- A terminal state name (`str`) among the final labels listed in §6.2, or `None` on unreachable combinations.

### Error Handling
- Construction can indirectly fail if `RegexTokenizer` cannot open or parse `keywords.json` (e.g., `FileNotFoundError`, `JSONDecodeError`). These are raised by the tokenizer; `ContentDFA` does not catch them.
- `process_text` expects a valid string and should not raise under normal operation.

### Side Effects
- No writes. The tokenizer reads configuration once at construction time.

### Thread Safety
- The instance holds mutable state (`self.state` and the nested `DirectionalityDFA`). Use one instance per thread/task or add external synchronization.

---

## 11. Test Plan
### 11.1 Unit Tests (pytest)
| ID | Scenario | Input | Expected |
|---|---|---|---|
| T1 | No triggers | `"Hello"` | `qF_Safe` |
| T2 | Badword→Others | `"you ... <badword>"` | `qF_Hate` |
| T3 | Badword→Self | `"I am <badword>"` | `qF_Offensive` |
| T4 | Politics only | `"Election debate"` (POLITIC) | `qF_Safe` |
| T5 | Sexword→Generic | `"explicit content"` (SEXWORD) | `qF_Sex` |
| T6 | Sexword→Others | `"you ... <sexword>"` | `qF_Harass` |
| T7 | Violence→Self | `"I want to <violence>"` | `qF_SelfHarm` |
| T8 | Violence→Others | `"we will <violence> you"` | `qF_Threats` |
| T9 | Violence→Generic | `"violence occurs"` | `qF_Violence` |
| T10 | Politics+Badword→Others | `"political <badword>"` | `qF_Hate` |
| T11 | Politics+Badword→Self | `"I ... political <badword>"` | `qF_Offensive` |
| T12 | Politics+Violence→Others | `"political <violence>"` | `qF_Hate` |
| T13 | Politics+Violence→Self | `"I ... political <violence>"` | `qF_Violence` |
| T14 | Idempotence | run twice | same label |
| T15 | Σ stability | add neutral words | same label |

*Implementation note:* For deterministic tests, either mock `RegexTokenizer` to emit known token sequences or feed synthetic tokens directly through `transition()` and `directionality_dfa.transition()` and then call `end_of_input()`.

### 11.2 Property‑Based Checks (optional)
- **Idempotence:** `process_text(process_text(s)) == process_text(s)` for arbitrary `s` mapped to labels (labels are idempotent under re‑classification of text, assuming tokenizer behavior is pure).  
- **Σ Closure:** Inserting/removing Σ tokens does not change the final label.

---

## 12. Appendix: Full Control Tables
### 12.1 Content Transition Table
| From \ Token | BADWORD | POLITIC | SEXWORD | VIOLENCE | Σ |
|---|---:|---:|---:|---:|---:|
| `q0`  | `qB` | `qP` | `qS` | `qV` | `q0` |
| `qB`  | `qB` | `qPB`| `qB` | `qB` | `qB` |
| `qP`  | `qPB`| `qP` | `qP` | `qPV`| `qP` |
| `qS`  | `qS` | `qS` | `qS` | `qS` | `qS` |
| `qV`  | `qV` | `qPV`| `qV` | `qV` | `qV` |
| `qPB` | `qPB`| `qPB`| `qPB`| `qPB`| `qPB` |
| `qPV` | `qPV`| `qPV`| `qPV`| `qPV`| `qPV` |

### 12.2 Final Mapping Table
| Content \ Direction | `qF_Self` | `qF_Others` | `qF_Generic` |
|---|---|---|---|
| `q0`  | `qF_Safe` | `qF_Safe` | `qF_Safe` |
| `qB`  | `qF_Offensive` | `qF_Hate` | `qF_Hate` |
| `qP`  | `qF_Safe` | `qF_Safe` | `qF_Safe` |
| `qS`  | `qF_Sex` | `qF_Harass` | `qF_Sex` |
| `qV`  | `qF_SelfHarm` | `qF_Threats` | `qF_Violence` |
| `qPB` | `qF_Offensive` | `qF_Hate` | `qF_Hate` |
| `qPV` | `qF_Violence` | `qF_Hate` | `qF_Hate` |
