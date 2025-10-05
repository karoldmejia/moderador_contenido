# Post Transform — Module Design Document
**File:** `post_transform.py`  
**Date:** 2025-10-04  
**Language:** Python 3.8+  
**Status:** Stable

---

## 1. Abstract
This module turns raw user posts into HTML by applying two layers:
1) **Regex-based enhancement**: emoticon → emoji substitution, link autolinking, and inline markup for mentions and hashtags.  
2) **TextX-based structural rendering**: parsing a custom DSL (defined in `post.tx`) and emitting HTML for rich constructs (bold/italic/underline/font tags and math-like formulas: fractions, roots, subscripts/superscripts, grouped expressions).

The output is a dictionary containing the generated HTML and a list of applied enhancements. The design favors explicit transformations, deterministic behavior, and clear separation between surface-level regex edits and grammar-driven rendering.

---

## 2. Scope and Non‑Goals
**In scope**
- Replace common ASCII emoticons with Unicode emojis.
- Autolink `http(s)://` URLs, wrap `@mentions` and `#hashtags` with spans.
- Parse a domain-specific language (`post.tx`) and render structural parts into HTML.

**Out of scope**
- Sanitization/escaping against HTML/script injection (callers should sanitize or extend the module).
- Resilient parsing for invalid DSL (errors currently bubble up from TextX).
- Styling/theming beyond minimal inline examples (CSS is expected upstream).

---

## 3. Glossary
- **DSL**: A small domain-specific language for post formatting defined in `post.tx` and compiled by TextX.
- **Part**: A parsed unit from the DSL (e.g., `Bold`, `Italic`, `Underline`, `Font`, `Formula`, `Text`, `Mention`, `Hashtag`, `Link`).
- **Formula Node**: A math-like AST node (`Frac`, `Sqrt`, `SubSup`, `Group`, `Expr`, `Formula`).

---

## 4. External Dependencies and Artifacts
- **Standard library**: `re`
- **Third‑party**:  
  - `textX` (`metamodel_from_file`) — compiles the grammar and parses posts.  
  - `pyparsing` — a transitive dependency of TextX; **do not** import `Path` from here.
- **Grammar file**: `post.tx` — located alongside the module.
- **Known import issue**: The code currently has `from pyparsing import Path`. This is incorrect and will shadow the real `Path`. **Fix** to:
  ```python
  from pathlib import Path
  ```

---

## 5. Public API
### 5.1 Function: `enhance_post(text: str) -> dict`
**Intent:** Apply lightweight regex transformations prior to grammar parsing.

**Behavior**
- **Emoticons → Emojis**: Replaces a predefined set (e.g., `":-)" → "😊"`, `":(" → "😢"`, `";-)" → "😉"`, `":D" → "😃"`, `"XD" → "😆"`, etc.).
- **Links**: Wraps `http(s)://...` in `<a href='…' target='_blank'>…</a>`.
- **Mentions**: Wraps `@word` in `<span class='mention'>…</span>`.
- **Hashtags**: Wraps `#word` in `<span class='hashtag'>…</span>`.
- Records human‑readable notes in `"enhancements"` (e.g., `"Emoji ':-)' → '😊'"`).

**Signature**
```python
def enhance_post(text: str) -> dict:
    return {"text": <html_like_str>, "enhancements": list[str]}
```

---

### 5.2 Function: `render_formula(node) -> str`
**Intent:** Convert a formula AST node (from TextX) to inline HTML.

**Supported nodes**
- `Frac(num, den)` → `<span class='frac'><span class='num'>…</span>/<span class='den'>…</span></span>`
- `Sqrt(index?, value)` → `√<sup>{index}</sup>({value})` or `√({value})`
- `SubSup(base, sup?, sub?)` → `base<sup>…</sup><sub>…</sub>`
- `Group(expr)` → `({render_formula(expr)})`
- `Expr(terms[], op[])` → concatenation of term HTML with infix operators
- `Formula(expr)` → delegates to `render_formula(expr)`
- Tokens like identifiers/ints and raw strings are stringified

**Signature**
```python
def render_formula(node) -> str:
    ...
```

---

### 5.3 Function: `render_part(part, enhancements: list[str]) -> str`
**Intent:** Render a single DSL `part` into HTML and optionally append a description to `enhancements`.

**Supported parts**
- `Bold` → `<b>…</b>` (source text derived from `part._tx_frozen_str.strip("*")`)
- `Italic` → `<i>…</i>` (strips `-` from ends)
- `Underline` → `<u>…</u>` (strips `_` from ends)
- `Font` → `<span style='font-family:cursive'>…</span>` (strips `/`)
- `Formula` → `<span class='formula'>{render_formula(part)}</span>`
- `Mention` / `Hashtag` / `Link` / `Text` → raw `part._tx_frozen_str`
- Fallback → `str(part)`

**Signature**
```python
def render_part(part, enhancements: list[str]) -> str:
    ...
```

---

### 5.4 Function: `transform_post(text: str) -> dict`
**Intent (Main Function):** Full pipeline: regex enhancement → DSL parse → HTML rendering.

**Algorithm**
1. `regex_result = enhance_post(text)`  
2. `preprocessed_text = regex_result["text"]` and `enhancements = regex_result["enhancements"]`
3. `model = post_mm.model_from_str(preprocessed_text)` (TextX parse; **no fallback**)
4. `html_parts = [render_part(p, enhancements) for p in model.parts]`
5. `html = " ".join(html_parts)`
6. `return {"text": html, "enhancements": enhancements}`

**Signature**
```python
def transform_post(text: str) -> dict:
    ...
```

---

## 6. Architecture & Data Flow
```
[Raw text]
   │
   ├─ enhance_post (regex)
   │     ├─ emoticons→emojis
   │     ├─ autolink URLs
   │     ├─ wrap @mentions / #hashtags
   │     └─ record enhancements
   │
   ├─ TextX parse (post.tx → post_mm) ──► AST(parts)
   │
   └─ render_part per AST node ──► HTML fragments ──► join ──► HTML
```

- **Parsing**: `post_mm = metamodel_from_file(str(Path(__file__).parent / "post.tx"))` at import time.
- **I/O**: Reads the grammar file once; all other work is in memory.
- **Thread‑safety**: Pure functions except for the module‑level `post_mm` (which is read‑only after creation).

---

## 7. Correctness Arguments
- **Determinism**: For a given input and grammar, the same HTML is produced.
- **Separation of concerns**: Surface regex edits are performed **before** grammar parsing to simplify the DSL and reduce ambiguity in the grammar.
- **Explicit rendering**: Each AST node class is mapped to a well‑defined HTML fragment; there is no hidden behavior.

---

## 8. Security, Escaping, and Safety
- **HTML injection risk**: `render_part` and `render_formula` insert text values directly into HTML. If attackers can control `part._tx_frozen_str` or identifier names, they may inject HTML/JS.  
  **Mitigation**: escape user‑controlled content (e.g., `html.escape`) and whitelist allowed attributes.
- **Autolink attributes**: `<a target='_blank'>` should include `rel="noopener noreferrer"` to prevent tab‑nabbing.
- **URL scheme**: restrict to `http`/`https` (current regex already does) and consider validating the URL before rendering.
- **CSS classes**: Ensure `.mention`, `.hashtag`, `.formula`, `.frac .num/.den` are defined in the consuming application’s stylesheet.

---

## 9. Edge Cases & Notes
- **Enhancement flags**: `"Link detected"`, `"Mention detected"`, `"Hashtag detected"` are appended **unconditionally**. Use `re.subn` or `re.findall` to append only when a match occurs.
- **Emoticon replacement order**: Overlaps like `":-)"` vs `":)"` should be applied longest‑first to avoid double replacement. The current loop uses `dict.items()` iteration; ensure it’s ordered accordingly.
- **Case sensitivity**: Emoticons like `"xd"` are not matched; only `"XD"` is handled.
- **Spacing in final HTML**: `html = " ".join(html_parts)` introduces a space between parts; if the DSL already preserves spacing, consider `"".join(...)`.
- **Grammar failures**: `post_mm.model_from_str` raises a `TextXError` on invalid input; there is no fallback rendering path. Consider a try/except that returns the regex‑enhanced text when parsing fails.
- **Import bug**: Replace `from pyparsing import Path` with `from pathlib import Path` to avoid NameError and file path issues.


---

## 10. Test Plan
### 10.1 Unit Tests (pytest)
| ID | Area | Input | Expected |
|---|---|---|---|
| T1 | Emoticon | `"ok :-)"` | `"😊"` present; enhancement note contains `"Emoji ':-)' → '😊'"` |
| T2 | Link | `"see https://a.b"` | `<a href='https://a.b' target='_blank'>https://a.b</a>` present *(consider rel attr)* |
| T3 | Mention | `"hi @bob"` | `<span class='mention'>@bob</span>` present |
| T4 | Hashtag | `"great #news"` | `<span class='hashtag'>#news</span>` present |
| T5 | Multiple emojis | `":) :("` | both replacements appear |
| T6 | No unconditional flags | `"plain"` | no “Link/Mention/Hashtag detected” when no matches |
| T7 | Import path | — | importing module with `from pathlib import Path` succeeds |
| T8 | Formula frac | DSL creating `Frac(1,2)` | HTML contains `<span class='frac'>` with `num` and `den` |
| T9 | Sqrt with index | DSL creating `Sqrt(index=3, value=x)` | HTML contains `√<sup>3</sup>(x)` |
| T10 | Sub/Sup | DSL creating `SubSup("x", sup="2")` | HTML contains `x<sup>2</sup>` |
| T11 | Group/Expr | DSL `(a+b)-c` | Operators interleaved with terms |
| T12 | Integration | Mixed post with DSL | Returned dict has `"text"` HTML and non-empty `"enhancements"` |

---

