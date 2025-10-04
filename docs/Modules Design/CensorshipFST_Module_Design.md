# CensorshipFST — Module Design Document
**File:** `censorship_fst.py`  
**Date:** 2025‑10‑05  
**Language:** Python 3.8+  
**Status:** Stable

---

## 1. Abstract
This module implements a length‑preserving word censorship mechanism. Given an input string, it replaces any disallowed word contained in configured blocklists with a same‑length sequence of asterisks (`*`). Non‑alphabetic characters, whitespace, and punctuation remain unchanged. The module is designed for deterministic behavior, predictable performance, and minimal dependencies.

---

## 2. Scope and Non‑Goals
**In scope**
- Censoring full words that appear in blocklists loaded from a local JSON file.
- Case‑insensitive matching by lowercasing the candidate word.
- Length‑preserving masking for censored words only.
- Deterministic single‑pass processing of a single string.

**Out of scope**
- Phrase matching, stemming, lemmatization, or fuzzy matching.
- Tokenization rules beyond `str.isalpha()` (digits/hyphens split words).
- Streaming I/O, concurrency primitives, or hot‑reloading of blocklists.
- CLI interface and logging (may be added by callers).

---

## 3. Glossary
- **Word**: A maximal contiguous run of characters where `char.isalpha()` is `True`. Any non‑alphabetic character (digits, punctuation, symbols, whitespace) terminates a word.
- **Blocklist**: A set of lowercased tokens that must be censored when matched as complete words.
- **Length‑preserving masking**: Replacement of each character of a censored word with `*`, with equal output length to the original word’s length.

---

## 4. External Dependencies and Artifacts
- **Standard library**: `pathlib.Path`, `json`
- **Data file**: `data/keywords.json` (located alongside the module).  
  Expected schema:
  ```json
  {
    "badwords":   ["..."],
    "sexwords":   ["..."],
    "violence":   ["..."]
  }
  ```
  Missing keys default to empty lists. Tokens are converted to lowercase on load.

---

## 5. Public API
### 5.1 Class: `CensorshipFST`
Intent: Represents a simple finite‑state style text filter with explicit state labels for clarity (`q0`, `qC`, `qF`).

**Constructor**
```python
CensorshipFST()
```
- Loads and normalizes blocklists from `data/keywords.json`.
- Initializes state labels and sets current state to `q0`.

**Primary Method (Main Function)**
```python
process_text(self, text: str) -> str
```
- **Role**: Principal entrypoint that performs the entire censorship algorithm over a single input string.
- **Input**: `text` — arbitrary Unicode string.
- **Output**: A new string where any disallowed word is replaced by a same‑length `*` sequence. Non‑alphabetic characters are passed through unchanged.
- **Determinism**: Given the same `text` and the same loaded blocklists, the output is deterministic.
- **Preconditions**: The keywords file must have been loaded successfully at construction.
- **Postconditions**:
  - Words that match the blocklists (case‑insensitive) are masked.
  - Words not in the blocklists are preserved exactly.
  - Non‑alphabetic characters are preserved exactly.
  - Leading/trailing whitespace **may be trimmed** due to `.strip()` at the end of the method.
- **Time/Space Complexity**: `O(n)` time, `O(1)` auxiliary space (aside from small buffers).

**Auxiliary Method**
```python
reset(self) -> None
```
- Sets internal state to `q0`. Invoked by `process_text` before processing and available for explicit external resets if an instance is reused.

> **Note**: The implementation does not declare standalone helper functions. However, conceptually, `process_text` embeds three internal responsibilities that can be extracted if needed (see §7).

---

## 6. Data Structures and State
- **Blocklists**: `self.badwords`, `self.sexwords`, `self.violence` — each is a `set[str]` of lowercased tokens.
- **State labels**: `q0` (normal), `qC` (censoring), `qF` (final).
- **Runtime state**:
  - `self.state`: current state label. Mutated within `process_text` and set to `qF` at completion.
  - Local variables within `process_text`: `output` (list of string fragments), `word_buffer` (list of letters), `i` (index), `char` (current character).

**Invariants**
- During processing, when a word has been recognized:
  - If the lowercased word is a blocklisted token, the emitted fragment has the same length as the original word and consists only of `*` characters.
  - Otherwise, the emitted fragment equals the original word byte‑for‑byte.
- Non‑alphabetic characters are emitted unchanged at their original positions relative to words.
- `qC` is a transient label; the method immediately returns to `q0` after emitting the mask.

---

## 7. Algorithm and Control Flow
### 7.1 High‑Level Flow
1. `reset()` → `state = q0`.
2. Append one space to `text` to guarantee a trailing word boundary.
3. Iterate with index `i` across `text`:
   - If `text[i].isalpha()`:
     1. Read a contiguous run of alphabetic characters into `word_buffer`.
     2. Convert to `word = "".join(word_buffer)` and `word_lower = word.lower()`.
     3. If `word_lower` is in any blocklist: set `state = qC`, append `"*"` × `len(word)` to `output`, set `state = q0`.
     4. Else: append `word` to `output`.
     5. If next character exists and is non‑alphabetic, append it and advance `i`.
   - Else:
     - Append the non‑alphabetic character as is and advance `i`.
4. Set `state = qF` and return `"".join(output).strip()`.



### 7.32Correctness Arguments
- **Length preservation (censored words)**: For any censored word `w`, the algorithm emits exactly `len(w)` asterisks. Therefore, intra‑word character positions are preserved in length, maintaining visual alignment for monospaced logs.
- **Transparency (safe words & separators)**: Words not present in blocklists and all non‑alphabetic characters are appended unchanged, preserving original content where censorship is not required.
- **Case‑insensitive matching**: Converting candidate words to lowercase before membership tests ensures matches across case variants while re‑emitting the original casing for safe words.
- **Idempotence under repeated application**: The output contains no alphabetic characters in masked segments (only `*`), and `*` is non‑alphabetic; running `process_text` again yields the same result.
- **Word boundary semantics**: The set of alphabetic characters is Unicode‑aware; diacritics count as alphabetic. Digits, hyphens, and underscores partition words, preventing accidental censorship of mixed tokens (e.g., `h4te`).

---

## 8. Auxiliary Responsibilities (Conceptual Helpers)
Although not implemented as separate functions, `process_text` internally performs the following responsibilities, which can be factored into private helpers without changing behavior:

1. **Word Reader**
   ```python
   # Conceptual signature (private helper)
   _read_word(text: str, i: int) -> tuple[str, int]
   # Reads a maximal alphabetic run starting at index i; returns (word, next_index).
   ```

2. **Blocklist Predicate**
   ```python
   _is_disallowed(token: str, bad: set[str], sex: set[str], vio: set[str]) -> bool
   # Returns True if token.lower() is in any of the three sets.
   ```

3. **Mask Emitter**
   ```python
   _emit_mask(n: int) -> str
   # Returns '*' * n
   ```

This factoring improves unit test coverage granularity and readability, and allows targeted optimization (e.g., consolidating blocklists into a single set).

---

## 9. Interfaces and Contracts
### 9.1 Inputs
- `text: str` — may contain any Unicode characters. Empty string is allowed.

### 9.2 Outputs
- A `str` of censored content. For censored words, masks have the same length as the matched word; for safe content and separators, the output reproduces the original characters.

### 9.3 Error Handling
- Constructor may raise:
  - `FileNotFoundError` when `data/keywords.json` is missing.
  - `json.JSONDecodeError` for malformed JSON.
- `process_text` assumes a valid string input and does not raise under normal conditions.

### 9.4 Side Effects
- Reads a file once during construction; no further I/O during processing.

### 9.5 Thread Safety
- Instances hold mutable `state`. Do not share a single instance across threads without external synchronization. Prefer one instance per thread/task.

---

---

---

## 15. Test Plan
### 15.1 Unit Tests (pytest)
| ID | Scenario | Input | Precondition | Expected Output |
|---|---|---|---|---|
| T1 | Empty input | `""` | — | `""` |
| T2 | Safe text unchanged | `"Hello world!"` | no overlaps in blocklists | `"Hello world!"` |
| T3 | Badword masking | `"You are a stupid person"` | `"stupid"` in badwords | `"You are a ****** person"` |
| T4 | Sexword masking | `"He watched porn last night"` | `"porn"` in sexwords | `"He watched **** last night"` |
| T5 | Violence masking | `"They will kill him"` | `"kill"` in violence | `"They will **** him"` |
| T6 | Multiple offensive words | `"dumb idiot!"` | both in badwords | `"**** *****!"` |
| T7 | Case‑insensitive | `"BadWord"` | `"badword"` in any list | `"*******"` |
| T8 | Punctuation boundary | `"idiot!"` | `"idiot"` in badwords | `"*****!"` |
| T9 | Hyphen split | `"re-entry"` | `"re"` not in lists | `"re-entry"` |
| T10 | Leading/trailing spaces | `"  stupid  "` | `"stupid"` in badwords | `"******"` (note whitespace trimmed) |
| T11 | Missing keywords file | — | remove/move JSON | constructor raises `FileNotFoundError` |
| T12 | Malformed JSON | — | break JSON syntax | constructor raises `json.JSONDecodeError` |


### 15.2 Property‑Based Checks (optional)
- Idempotence: `process_text(process_text(s)) == process_text(s)` for arbitrary `s`.
- Non‑alphabetic transparency: Removing all alphabetics from `s` yields identical sequences in input and output.

---




