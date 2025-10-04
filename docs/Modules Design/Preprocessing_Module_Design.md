# RegexTokenizer — Module Design Document
**File:** `preprocessing.py` (class `RegexTokenizer`)  
**Date:** 2025-10-03  
**Language:** Python 3.8+  
**Status:** Stable

---

## 1. Abstract
`RegexTokenizer` converts raw text into a **sequence of symbolic tokens** suitable for downstream DFAs. It loads keyword lexicons from a JSON file, performs **emoji separation**, **multi‑word phrase replacement** (`SPAMWORD`, `FAKECLAIM`), and then classifies each whitespace‑delimited unit as one of several token classes (URLs, hashtags, mentions, content cues, pronouns, auxiliaries, emojis, generic words). The design favors determinism, low dependencies, and easy maintenance via a single JSON configuration.

---

## 2. Scope and Non‑Goals
**In scope**
- Load keyword sets from a JSON file and hold them in memory as Python containers.
- Normalize and scan text to produce token classes needed by DFAs (content and directionality).
- Detect multi‑word phrases via word‑boundary regex replacement (case‑insensitive).
- Detect emojis within the Unicode range U+1F300–U+1FAFF and classify negative emojis from a curated set.

**Out of scope**
- POS tagging, lemmatization, stemming, or syntactic parsing.
- Named‑entity recognition or semantic similarity.
- Overlapping phrase resolution beyond longest‑first order within each list.
- Locale‑specific orthography normalization beyond `lower()` checks.

---

## 3. Glossary
- **Phrase**: Multi‑word string that should be collapsed into a single symbolic token (e.g., a spam slogan).
- **Symbolic token**: A label like `BADWORD`, `SEXWORD`, `PRONOUN_SELF`, `URL`, etc.
- **Σ (Sigma)**: Any token not used by DFAs for transitions; emitted as `WORD` here.
- **Negative emoji**: Emoji considered harmful/negative by configuration, emitted as `NEG_EMOJI`.

---

## 4. External Dependencies and Artifacts
- **Standard library**: `re`, `json`
- **Data file**: `keywords.json` (path passed in the constructor).  
  **Expected keys** (minimal contract):
  ```json
  {
    "badwords": [], "sexwords": [], "violence": [],
    "spamwords": [], "fakeclaims": [], "politics": [],
    "pronouns": [], "pronouns_self": [], "pronouns_other": [], "pronouns_group": [],
    "aux_verbs": [], "bademojis": []
  }
  ```
  Missing keys will raise `KeyError` at load time in current implementation.

---

## 5. Public API
### 5.1 Class: `RegexTokenizer`
**Intent:** Convert text to a deterministic token sequence driven by configurable lexicons and regex rules.

**Constructor**
```python
RegexTokenizer(keywords_file: str = "keywords.json")
```
- Loads JSON and initializes internal containers:
  - Sets: `badwords`, `sexwords`, `violence`, `politics`, `pronouns`, `pronouns_self`, `pronouns_other`, `pronouns_group`, `aux_verbs`, `bad_emojis`.
  - Lists sorted by **descending length**: `spamwords`, `fakeclaims` (to prefer longest phrase match first).
- Compiles regex patterns:
  - `URL`: `r"(https?:\/\/[^\s]+)"` (fullmatch used)
  - `HASHTAG`: `r"(#[\w\d_]+)"`
  - `MENTION`: `r"(@[\w\d_]+)"`
  - `WORD`: `r"\b[a-zA-Z]+\b"`
  - `EMOJI`: `r"[\U0001F300-\U0001FAFF]"`

**Methods**
```python
replace_phrases(self, text: str, phrases: list[str], token: str) -> str
```
- Replaces each phrase with `token`, using **word boundaries** and **case‑insensitive** matching:
  - Pattern: `r'\b' + re.escape(phrase) + r'\b'` with `re.IGNORECASE`.
  - Returns the modified text.

```python
separate_emojis(self, text: str) -> str
```
- Surrounds any emoji matched by `EMOJI` with spaces (`" <emoji> "`), helping subsequent `split()` to isolate them.

```python
tokenize(self, text: str) -> list[str]
```
- Full pipeline; see §6 for details.

---

## 6. Tokenization Pipeline
1. **Emoji separation**  
   `text = separate_emojis(text)` — inserts spaces around emoji code points in `[\U0001F300-\U0001FAFF]`.

2. **Phrase replacement**  
   - `text = replace_phrases(text, spamwords, "SPAMWORD")`  
   - `text = replace_phrases(text, fakeclaims, "FAKECLAIM")`  
   Phrases are processed **longest first** to reduce partial matches.

3. **Whitespace split**  
   `for word in text.split():` — iterate over whitespace‑separated units.

4. **Token classification (in priority order)**  
   For each `word`:
   - **URL**: if `URL.fullmatch(word)` → `URL`
   - **HASHTAG**: if `HASHTAG.match(word)` → `HASHTAG`
   - **MENTION**: if `MENTION.match(word)` → `MENTION`
   - **Content cues (substring check)**:
     - if `any(bw in word_lower for bw in badwords)` → `BADWORD`
     - elif `any(sw in word_lower for sw in sexwords)` → `SEXWORD`
     - elif `any(v in word_lower for v in violence)` → `VIOLENCE`
     - elif `any(p in word_lower for p in politics)` → `POLITIC`
   - **Pronouns** (exact membership):
     - `word_lower in pronouns_self` → `PRONOUN_SELF`
     - `word_lower in pronouns_other` → `PRONOUN_OTHER`
     - `word_lower in pronouns_group` → `PRONOUN_GROUP`
     - `word_lower in pronouns` → `PRONOUN`
   - **Auxiliaries**: `word_lower in aux_verbs` → `AUX_VERB`
   - **Multi‑word markers**: `word in {"SPAMWORD","FAKECLAIM"}` → emit as‑is
   - **Emoji**: `EMOJI.match(word)` → `NEG_EMOJI` if `word in bad_emojis` else `EMOJI`
   - **Generic words**: if `WORD.match(word)` → `WORD`
   - **Fallback**: `WORD`

**Note on substring matching**: Content cues (`BADWORD`, `SEXWORD`, `VIOLENCE`, `POLITIC`) use **substring containment**, not exact word matching. Thus, `"foobar"` triggers if `"bar"` is in the corresponding set. See §10 (Limitations).

---

## 7. Token Classes Emitted
| Class | Description | Source |
|---|---|---|
| `URL` | Absolute link beginning with `http://` or `https://` | Regex `fullmatch` |
| `HASHTAG` | `#` followed by word chars/digits/underscore | Regex `match` |
| `MENTION` | `@` followed by word chars/digits/underscore | Regex `match` |
| `BADWORD` | Any token whose lowercase form **contains** an item from `badwords` | Substring search |
| `SEXWORD` | Contains an item from `sexwords` | Substring search |
| `VIOLENCE` | Contains an item from `violence` | Substring search |
| `POLITIC` | Contains an item from `politics` | Substring search |
| `PRONOUN_SELF` | Exact match in `pronouns_self` | Set membership |
| `PRONOUN_OTHER` | Exact match in `pronouns_other` | Set membership |
| `PRONOUN_GROUP` | Exact match in `pronouns_group` | Set membership |
| `PRONOUN` | Exact match in `pronouns` (generic) | Set membership |
| `AUX_VERB` | Exact match in `aux_verbs` | Set membership |
| `SPAMWORD` | Phrase collapsed to marker | Phrase replacement |
| `FAKECLAIM` | Phrase collapsed to marker | Phrase replacement |
| `NEG_EMOJI` | Emoji present in `bademojis` | Emoji + set membership |
| `EMOJI` | Emoji in U+1F300–U+1FAFF | Regex `match` |
| `WORD` | Alphabetic token (A–Z/a–z) | Regex `match` or fallback |

---

## 8. Regular Expressions
- `URL`: `(https?:\/\/[^\s]+)` — greedy to end of non‑space; accepts punctuation within.
- `HASHTAG`: `(#[\w\d_]+)` — anchored at start; permits alnum + underscore.
- `MENTION`: `(@[\w\d_]+)` — same constraints as hashtag, with `@` prefix.
- `WORD`: `\b[a-zA-Z]+\b` — ASCII letters only; accented or non‑Latin letters will **not** match here and will fall to `WORD` by fallback rule.
- `EMOJI`: `[\U0001F300-\U0001FAFF]` — single code‑point emojis in this block; multi‑codepoint sequences (skin tones, ZWJ) may not be fully captured as a unit.
---

## 9. Correctness and Design Rationale
- **Longest‑first phrase replacement**: Sorting `spamwords` and `fakeclaims` by descending length reduces partial overshadowing (e.g., replacing `"free money now"` before `"free"`).
- **Substring content matching**: Chosen to catch obfuscations like `"idi0t!!!"` if configured with partial tokens (e.g., `"idi"`), and to match concatenations `"killthem"` when the word list includes `"kill"`. This increases recall, with a trade‑off in precision (see §11).
- **Priority order**: URLs/hashtags/mentions are recognized before content cues to avoid misclassifying handles or hashtags that contain sensitive substrings.
- **Emoji separation**: Inserting spaces ensures emojis are tokenized even when adjacent to words or punctuation.
- **Determinism**: Given a fixed lexicon and regex set, the pipeline yields the same output for the same input.

---

## 10. Test Plan
### 10.1 Unit Tests (pytest)
| ID | Area | Input | Lexicon setup | Expected tokens |
|---|---|---|---|---|
| T1 | URL | `"Visit https://a.b/c"` | — | `["WORD","URL"]` |
| T2 | Hashtag | `"#Topic trending"` | — | `["HASHTAG","WORD"]` |
| T3 | Mention | `"@user hi"` | — | `["MENTION","WORD"]` |
| T4 | Badword substring | `"foobar"` | `badwords={"bar"}` | `["BADWORD"]` |
| T5 | Politics substring | `"political"` | `politics={"politic"}` | `["POLITIC"]` |
| T6 | Sexword | `"sexist"` | `sexwords={"sex"}` | `["SEXWORD"]` |
| T7 | Violence | `"kill-them"` | `violence={"kill"}` | `["VIOLENCE","WORD"]` |
| T8 | Pronoun self | `"I"` | `pronouns_self={"i"}` | `["PRONOUN_SELF"]` |
| T9 | Pronoun other | `"you"` | `pronouns_other={"you"}` | `["PRONOUN_OTHER"]` |
| T10 | Pronoun group | `"they"` | `pronouns_group={"they"}` | `["PRONOUN_GROUP"]` |
| T11 | Aux verb | `"is"` | `aux_verbs={"is"}` | `["AUX_VERB"]` |
| T12 | Spam phrase | `"free money now"` | `spamwords=["free money now"]` | `["SPAMWORD"]` |
| T13 | Fake claim | `"cure cancer fast"` | `fakeclaims=["cure cancer fast"]` | `["FAKECLAIM"]` |
| T14 | Emoji neg | `"😡"` | `bademojis={"😡"}` | `["NEG_EMOJI"]` |
| T15 | Emoji neutral | `"🙂"` | `bademojis={"😡"}` | `["EMOJI"]` |
| T16 | Mixed | `"@me free money now 😡"` | as above | `["MENTION","SPAMWORD","NEG_EMOJI"]` |


---