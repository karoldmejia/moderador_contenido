# Test Design – TextPipeline

This document describes the test design for the `TextPipeline` based on the provided `pytest` tests. Each case includes setup, input, expected output (warnings and/or rendering/censoring expectations), and a short description.

---

## TestTextPipeline 1 – Safe neutral text (no warnings)
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"Hello everyone! Have a great day :)"`

**Expected Output:**  
- `result["warnings"] == []`

**Description:**  
Validates that a neutral message with a smiley produces no warnings.

---

## TestTextPipeline 2 – Badword triggers hate-speech warning and censoring
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"You are a stupid person"`

**Expected Output:**  
- `"this post may contain hate speech" in result["warnings"]`  
- `"stupid" not in result["text"].lower()` (the bad word is censored)

**Description:**  
Checks that offensive language toward others yields a hate‑speech warning and masking in the rendered text.

---

## TestTextPipeline 3 – Sexual term triggers harassment warning and censoring
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"He watched porn last night"`

**Expected Output:**  
- `"this post may contain harassment" in result["warnings"]`  
- `"porn" not in result["text"].lower()`

**Description:**  
Ensures sexual content generates a harassment warning and is censored in the output text.

---

## TestTextPipeline 4 – Threatening language triggers threats warning and censoring
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"I will kill him if he comes"`

**Expected Output:**  
- `"this post may contain threats" in result["warnings"]`  
- `"kill" not in result["text"].lower()`

**Description:**  
Validates detection of explicit threats and censoring of violent terms.

---

## TestTextPipeline 5 – Spam density (many URLs) triggers spam warning
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"Check this out http://spam.com http://spam.com http://spam.com http://spam.com"`

**Expected Output:**  
- `"this post may contain spam" in result["warnings"]`

**Description:**  
Four URLs in one message should trigger a spam warning.

---

## TestTextPipeline 6 – Hashtags & mentions are safe
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"Hey @john, check out #Python #AI"`

**Expected Output:**  
- `result["warnings"] == []`

**Description:**  
Confirms that hashtags and mentions alone do not raise warnings.

---

## TestTextPipeline 7 – LaTeX fraction is rendered
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"The fraction is $\frac{x+1}{y-1}$"`

**Expected Output:**  
- `result["warnings"] == []`  
- `"<span class='frac'>" in result["text"]` (HTML rendering of the fraction)

**Description:**  
Ensures math content is converted to HTML without generating moderation warnings.

---

## TestTextPipeline 8 – Badword + sexual term: hate-speech warning and censoring
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"You are a stupid idiot and watched porn"`

**Expected Output:**  
- `"this post may contain hate speech" in result["warnings"]`  
- `"stupid" not in result["text"].lower()`  
- `"porn" not in result["text"].lower()`

**Description:**  
Multiple sensitive categories present; test asserts at least the hate‑speech warning and that both terms are censored.

---

## TestTextPipeline 9 – Violence wording w/ pronouns → violence warning and censoring
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"They should die for this crime"`

**Expected Output:**  
- `"this post may contain violence" in result["warnings"]`  
- `"die" not in result["text"].lower()`

**Description:**  
Generic violence (not direct threat syntax) should raise a violence warning and censor the violent verb.

---

## TestTextPipeline 10 – Mixed elements: link render, hashtag/mention visible, emoji replacement, and hate-speech warning
**SetUp:**  
`pipeline = TextPipeline()`

**Input:**  
`"Wow :) visit http://site.com #fun @alice you dumb"`

**Expected Output:**  
- `"this post may contain hate speech" in result["warnings"]`  
- `"dumb" not in result["text"].lower()`  
- `"<a href=" in result["text"]` (URL is rendered as a link)  
- `"#fun" in result["text"]` (hashtag remains visible)  
- `"@alice" in result["text"]` (mention remains visible)  
- `"😊" in result["text"]` (smiley → emoji replacement)

**Description:**  
End‑to‑end rendering and moderation: anchor tags for URLs, preserved social markup, emoji substitution, and censoring of offensive terms with appropriate warning.

---

*End of document.*
