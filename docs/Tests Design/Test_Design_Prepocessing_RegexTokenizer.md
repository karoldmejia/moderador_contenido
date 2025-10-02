# Test Design – RegexTokenizer

This document presents the test design based on the provided `pytest` tests for `RegexTokenizer`. Each test case includes the setup, the input text, the expected token sequence, and a brief description of what is validated.

---

# 1. Unit tests

## TestRegexTokenizer 1 – Badword recognized
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"stupid"`

**Expected Output:**  
`["BADWORD"]`

**Description:**  
Verifies that a known bad word is normalized and emitted as the `BADWORD` token.

---

## TestRegexTokenizer 2 – Sexual word recognized
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"porn"`

**Expected Output:**  
`["SEXWORD"]`

**Description:**  
Ensures sexual vocabulary maps to the `SEXWORD` token.

---

## TestRegexTokenizer 3 – Violence word recognized
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"kill"`

**Expected Output:**  
`["VIOLENCE"]`

**Description:**  
Checks that violent vocabulary is recognized as `VIOLENCE`.

---

## TestRegexTokenizer 4 – Spam phrase recognized
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"buy now"`

**Expected Output:**  
`["SPAMWORD"]`

**Description:**  
Validates multi-token spam phrase collapsing into the single `SPAMWORD` token.

---

## TestRegexTokenizer 5 – Fake claim recognized
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"miracle cure"`

**Expected Output:**  
`["FAKECLAIM"]`

**Description:**  
Confirms health-misinformation phrase is normalized to `FAKECLAIM`.

---

## TestRegexTokenizer 6 – Politics keyword recognized
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"democrats"`

**Expected Output:**  
`["POLITIC"]`

**Description:**  
Ensures political keywords are mapped to `POLITIC` (singular normalized label).

---

## TestRegexTokenizer 7 – Pronouns (self and other)
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"i you"`

**Expected Output:**  
`["PRONOUN_SELF", "PRONOUN_OTHER"]`

**Description:**  
Checks correct tagging for first-person and second-person pronouns.

---

## TestRegexTokenizer 8 – Normal words
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"hello world"`

**Expected Output:**  
`["WORD", "WORD"]`

**Description:**  
Verifies fallback classification for non-keyword tokens.

---

# 2. Emojis

## TestRegexTokenizer 9 – Positive emojis
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"😀 😃"`

**Expected Output:**  
`["EMOJI", "EMOJI"]`

**Description:**  
Ensures standard positive/neutral emojis are tagged as `EMOJI`.

---

## TestRegexTokenizer 10 – Negative emoji and explosion
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"💀 💥"`

**Expected Output:**  
`["NEG_EMOJI", "EMOJI"]`

**Description:**  
Validates that skull is treated as negative (`NEG_EMOJI`) and explosion remains generic `EMOJI`.

---

## TestRegexTokenizer 11 – Mixed emojis
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"😀 💀 😃 💥"`

**Expected Output:**  
`["EMOJI", "NEG_EMOJI", "EMOJI", "EMOJI"]`

**Description:**  
Checks proper alternation between `EMOJI` and `NEG_EMOJI` according to emoji polarity.

---

# 3. URL, hashtag, mention

## TestRegexTokenizer 12 – URLs
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"https://example.com http://test.com"`

**Expected Output:**  
`["URL", "URL"]`

**Description:**  
Verifies detection of both HTTPS and HTTP URLs.

---

## TestRegexTokenizer 13 – Hashtags
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"#python #pytest"`

**Expected Output:**  
`["HASHTAG", "HASHTAG"]`

**Description:**  
Ensures hashtag tokens are recognized and labeled as `HASHTAG`.

---

## TestRegexTokenizer 14 – Mentions
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"@user1 @user2"`

**Expected Output:**  
`["MENTION", "MENTION"]`

**Description:**  
Checks that `@`-prefixed handles are tagged as `MENTION`.

---

# 4. Mixed cases

## TestRegexTokenizer 15 – Mixed text with multiple categories
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"i stupid 😀 #fun @user https://test.com porn"`

**Expected Output:**  
`["PRONOUN_SELF", "BADWORD", "EMOJI", "HASHTAG", "MENTION", "URL", "SEXWORD"]`

**Description:**  
End-to-end path covering pronouns, badwords, emojis, hashtags, mentions, URLs, and sexual terms ordering.

---

## TestRegexTokenizer 16 – Mixed text with numbers and spam
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"us buy now 1234 #deal @shop 😀"`

**Expected Output:**  
`["PRONOUN_GROUP", "SPAMWORD", "WORD", "HASHTAG", "MENTION", "EMOJI"]`

**Description:**  
Validates proper grouping of “buy now” into `SPAMWORD`, numeric token fallback as `WORD`, and group pronoun tagging.

---

## TestRegexTokenizer 17 – Many emojis
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"😀😀😀😀😀😀"`

**Expected Output:**  
`["EMOJI", "EMOJI", "EMOJI", "EMOJI", "EMOJI", "EMOJI"]`

**Description:**  
Ensures contiguous emojis tokenize into repeated `EMOJI` labels.

---

## TestRegexTokenizer 18 – All categories together
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"you porn kill 💀 https://x.com #warning @user"`

**Expected Output:**  
`["PRONOUN_OTHER", "SEXWORD", "VIOLENCE", "NEG_EMOJI", "URL", "HASHTAG", "MENTION"]`

**Description:**  
Covers a broad combination of categories and their expected ordering.

---

## TestRegexTokenizer 19 – Adjacent tokens without spaces
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"hello😀buy now💀world"`

**Expected Output:**  
`["WORD", "EMOJI", "SPAMWORD", "NEG_EMOJI", "WORD"]`

**Description:**  
Asserts robustness when categories are adjacent to words/emojis without whitespace.

---

## TestRegexTokenizer 20 – Fake claims + politics + social
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"miracle cure democrats #vote @news"`

**Expected Output:**  
`["FAKECLAIM", "POLITIC", "HASHTAG", "MENTION"]`

**Description:**  
Confirms correct sequence when multiple special categories appear together.

---

## TestRegexTokenizer 21 – Only symbols
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"!@# $%^ &*()"`

**Expected Output:**  
`["WORD", "WORD", "WORD"]`

**Description:**  
Ensures unknown symbol chunks fall back to `WORD` tokens.

---

# 5. Edge cases

## TestRegexTokenizer 22 – Unknown symbols with digits
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"1234 !@#$"`

**Expected Output:**  
`["WORD", "WORD"]`

**Description:**  
Validates fallback classification to `WORD` for digits and symbol-only groups.

---

## TestRegexTokenizer 23 – Combined emojis and words (no spaces)
**SetUp:**  
`tokenizer = RegexTokenizer(keywords_file=Path(__file__).parent.parent / "src" / "data" / "keywords.json")`

**Input:**  
`"hello😀stupid💀"`

**Expected Output:**  
`["WORD", "EMOJI", "BADWORD", "NEG_EMOJI"]`

**Description:**  
Checks adjacent emoji-word boundaries with badword and negative-emoji detection.

---

*End of document.*
