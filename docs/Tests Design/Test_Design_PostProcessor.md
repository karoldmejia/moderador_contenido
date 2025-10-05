# Test Design – Post Processor Suite

This document captures the **test design** for the provided tests targeting the post‑processing layer:
- `enhance_post(text)`
- `render_formula(ast_node)`
- `render_part(part, enhancements)`
- `transform_post(text)` (integration)

Each case includes **SetUp**, **Input**, **Expected Output**, and a short **Description**.

---

## Section A — enhance_post

### TestPostProcessor 1 – Emoji replacement
**SetUp:**  
No special setup (pure function).

**Input:**  
`"Hello :-)"`

**Expected Output:**  
- `result["text"]` contains `😊`  
- `result["enhancements"]` contains an entry mentioning `"Emoji"`

**Description:**  
Verifies ASCII emoticon to emoji substitution and the corresponding enhancement note.

---

### TestPostProcessor 2 – Multiple emojis
**SetUp:**  
None.

**Input:**  
`"Nice :D and sad :-("`

**Expected Output:**  
- `result["text"]` contains `😃` and `😢`

**Description:**  
Ensures multiple emoticons are independently converted to their emoji counterparts.

---

### TestPostProcessor 3 – Link detection
**SetUp:**  
None.

**Input:**  
`"Visit https://example.com for more info"`

**Expected Output:**  
- `result["text"]` contains `<a href='https://example.com'`  
- `"Link detected"` appears in `result["enhancements"]`

**Description:**  
Validates URL recognition and HTML anchor rendering with an enhancement entry.

---

### TestPostProcessor 4 – Mention detection
**SetUp:**  
None.

**Input:**  
`"Hi @karol!"`

**Expected Output:**  
- `result["text"]` contains `<span class='mention'>@karol</span>`  
- `"Mention detected"` appears in `result["enhancements"]`

**Description:**  
Checks that `@handle` mentions become styled spans and are recorded as enhancements.

---

### TestPostProcessor 5 – Hashtag detection
**SetUp:**  
None.

**Input:**  
`"Loving the #sunset"`

**Expected Output:**  
- `result["text"]` contains `<span class='hashtag'>#sunset</span>`  
- `"Hashtag detected"` appears in `result["enhancements"]`

**Description:**  
Ensures hashtags are wrapped with a dedicated span and an enhancement note is logged.

---

### TestPostProcessor 6 – Combined features (mention + link + hashtag + emoji)
**SetUp:**  
None.

**Input:**  
`"Hey @user check this link https://example.com #wow :-)"`

**Expected Output:**  
- HTML includes `<span class='mention'>`, `<a href=`, `<span class='hashtag'>`  
- Text includes `😊`

**Description:**  
End‑to‑end check that multiple detectors can operate together in one pass.

---

## Section B — render_formula

### TestPostProcessor 7 – Render fraction
**SetUp:**  
Instantiate a `Frac` object with `num="x+1"`, `den="y-1"`.

**Input:**  
`render_formula(Frac())`

**Expected Output:**  
- HTML contains `<span class='frac'>`  
- Includes `x+1` and `y-1`

**Description:**  
Validates fraction layout using dedicated HTML markup.

---

### TestPostProcessor 8 – Render square root (no index)
**SetUp:**  
`Sqrt(value="9", index=None)`

**Input:**  
`render_formula(Sqrt())`

**Expected Output:**  
- Exact string: `√(9)`

**Description:**  
Checks √ formatting when no root index is provided.

---

### TestPostProcessor 9 – Render n‑th root (with index)
**SetUp:**  
`Sqrt(value="x", index="3")`

**Input:**  
`render_formula(Sqrt())`

**Expected Output:**  
- Exact string: `√<sup>3</sup>(x)`

**Description:**  
Validates superscript index rendering for n‑th roots.

---

### TestPostProcessor 10 – Render sub and sup
**SetUp:**  
`SubSup(base="x", sup="2", sub="i")`

**Input:**  
`render_formula(SubSup())`

**Expected Output:**  
- HTML contains `<sup>2</sup>` and `<sub>i</sub>`

**Description:**  
Ensures both superscript and subscript are emitted.

---

### TestPostProcessor 11 – Render grouped expression
**SetUp:**  
`Group(expr="a+b")`

**Input:**  
`render_formula(Group())`

**Expected Output:**  
- Exact string: `(a+b)`

**Description:**  
Confirms grouping with parentheses is preserved.

---

## Section C — render_part

### TestPostProcessor 12 – Bold formatting
**SetUp:**  
`part._tx_frozen_str = "*strong*"`; `enhancements = []`

**Input:**  
`render_part(part, enhancements)`

**Expected Output:**  
- Returns `"<b>strong</b>"`  
- `"Bold formatting"` appended to `enhancements`

**Description:**  
Verifies markdown‑like bold is converted to `<b>` and tracked as an enhancement.

---

### TestPostProcessor 13 – Italic formatting
**SetUp:**  
`part._tx_frozen_str = "-soft-"`; `enhancements = []`

**Input:**  
`render_part(part, enhancements)`

**Expected Output:**  
- Returns `"<i>soft</i>"`  
- `"Italic formatting"` recorded

**Description:**  
Checks italic conversion and enhancement logging.

---

### TestPostProcessor 14 – Underline formatting
**SetUp:**  
`part._tx_frozen_str = "_under_"`; `enhancements = []`

**Input:**  
`render_part(part, enhancements)`

**Expected Output:**  
- Returns `"<u>under</u>"`  
- `"Underline formatting"` recorded

**Description:**  
Ensures underline formatting is supported and noted.

---

### TestPostProcessor 15 – Font style (cursive) formatting
**SetUp:**  
`part._tx_frozen_str = "/ fancy /"`; `enhancements = []`

**Input:**  
`render_part(part, enhancements)`

**Expected Output:**  
- Returned HTML contains `font-family:cursive`  
- `"Font style"` recorded

**Description:**  
Validates custom font styling directive is applied and logged.

---

## Section D — transform_post (integration)

### TestPostProcessor 16 – Emojis, mentions, hashtags, links
**SetUp:**  
None.

**Input:**  
`"Hello @karol :-) visit https://example.com #peace"`

**Expected Output:**  
- HTML contains `<span class='mention'>@karol</span>`, `😊`, `<a href=`, `<span class='hashtag'>#peace</span>`  
- Enhancements include `"Link detected"` and `"Mention detected"`

**Description:**  
Integration test confirming combined rendering and enhancement recording.

---

### TestPostProcessor 17 – Valid formula rendered
**SetUp:**  
None.

**Input:**  
`"The fraction is $\frac{x+1}{y-1}$ and the result is great"`

**Expected Output:**  
- HTML contains `<span class='frac'>`  
- Enhancements include `"Formula rendering"`

**Description:**  
Checks valid LaTeX‑like formula detection and HTML rendering within the post.

---

### TestPostProcessor 18 – Invalid formula preserved
**SetUp:**  
None.

**Input:**  
`"Weird result: $(x++1)/(y--1)$ makes no sense"`

**Expected Output:**  
- The literal `"$(x++1)/(y--1)$"` appears unchanged in the output HTML

**Description:**  
Ensures syntactically invalid formulas are not transformed and remain intact.

---

### TestPostProcessor 19 – Mixed valid and invalid formulas
**SetUp:**  
None.

**Input:**  
`"Valid: $\frac{x}{y}$ but this one fails: $(x+1//y)$"`

**Expected Output:**  
- Output contains a rendered formula (`<span class='frac'>`, or `√`, or `<sup>`) for the valid part  
- The invalid literal `"$(x+1//y)$"` remains unchanged

**Description:**  
Verifies selective rendering: valid formulas are transformed, invalid ones are preserved.

---

*End of document.*
