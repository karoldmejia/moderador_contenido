# Test Design – SpamDFA

This document presents the test design derived from the provided `pytest` tests for `SpamDFA`. Each test case includes the setup, the input text, the expected final state, and a brief description of what is validated.

---

# Safe cases

## TestSpamDFA 1 – Empty input is safe
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`""`

**Expected Output:**  
`dfa.qSafe`

**Description:**  
Verifies that an empty string does not trigger spam detection.

---

## TestSpamDFA 2 – Single URL remains safe
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"Check out my blog at http://example.com"`

**Expected Output:**  
`dfa.qSafe`

**Description:**  
A message containing a single URL should be classified as safe.

---

## TestSpamDFA 3 – Two URLs remain safe
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"Visit http://site1.com and http://site2.com for details"`

**Expected Output:**  
`dfa.qSafe`

**Description:**  
Confirms that two URLs alone do not cross the spam threshold.

---

## TestSpamDFA 4 – Three hashtags remain safe
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"#fun #coding #python"`

**Expected Output:**  
`dfa.qSafe`

**Description:**  
Ensures that up to three hashtags are allowed without being flagged as spam.

---

## TestSpamDFA 5 – Mixed URLs and hashtags remain safe
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"http://abc.com #learn #code http://xyz.com"`

**Expected Output:**  
`dfa.qSafe`

**Description:**  
Validates that a mixed message with two URLs and two hashtags remains below spam limits.

---

# Direct spam cases

## TestSpamDFA 6 – Spamword “Click here” triggers spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"Click here to win a free iPhone!"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Confirms that typical spam call‑to‑action wording is classified as spam.

---

## TestSpamDFA 7 – Spamword “Buy now” triggers spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"Buy now, limited time offer!"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Another classic spam phrase should immediately yield a spam classification.

---

## TestSpamDFA 8 – Fake claims / guarantees trigger spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"This miracle cure is 100% proven and guaranteed"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Validates that health‑related fake claims and absolute guarantees are flagged as spam.

---

## TestSpamDFA 9 – Four URLs cross the spam threshold
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"http://a.com http://b.com http://c.com http://d.com"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Checks that a high density of URLs (≥4) is considered spam.

---

## TestSpamDFA 10 – Four hashtags cross the spam threshold
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"#promo #sale #discount #cheap"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Ensures that an excessive number of hashtags (≥4) is treated as spam.

---

# Mixed cases with spam

## TestSpamDFA 11 – URL followed by spamword becomes spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"Check this out http://abc.com and click here for details"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Despite containing a single URL (normally safe), the presence of a spamword (“click here”) makes the message spam.

---

## TestSpamDFA 12 – Hashtag with fake claim becomes spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"#health miracle cure revealed today"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Combining social markup with a fake‑claim phrase should be classified as spam.

---

## TestSpamDFA 13 – Three URLs plus fake claim becomes spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"http://a.com http://b.com http://c.com unbelievable secret formula"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
Even if three URLs alone might be safe, the added fake‑claim wording causes a spam classification.

---

## TestSpamDFA 14 – Two hashtags plus spamword becomes spam
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"#deal #promo get rich quick!"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
A spam trigger phrase (“get rich quick”) turns an otherwise borderline message into spam.

---

## TestSpamDFA 15 – Mixed safe pattern followed by spam phrase
**SetUp:**  
`dfa = SpamDFA()`

**Input:**  
`"http://abc.com #fun #coding http://xyz.com free money waiting"`

**Expected Output:**  
`dfa.qSpam`

**Description:**  
A message that would otherwise be safe (two URLs + two hashtags) becomes spam due to the final spam phrase (“free money waiting”).

---

*End of document.*
