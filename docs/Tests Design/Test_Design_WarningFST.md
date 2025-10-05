# Test Design – WarningFST

This document describes the **test design** for the `WarningFST` based on the provided `pytest` tests. Each case includes the setup, the input passed to `generate_warning(final_state)`, the expected output (warning string or `None`), and a brief description.

---

# Individual state mappings

## TestWarningFST 1 – Spam state maps to spam warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qSpam"`

**Expected Output:**  
`"this post may contain spam"`

**Description:**  
Verifies correct mapping of the spam final state to its user‑facing warning.

---

## TestWarningFST 2 – Offensive state maps to offensive-language warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Offensive"`

**Expected Output:**  
`"this post may contain offensive language"`

**Description:**  
Checks mapping for content classified as offensive language.

---

## TestWarningFST 3 – Hate state maps to hate-speech warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Hate"`

**Expected Output:**  
`"this post may contain hate speech"`

**Description:**  
Ensures hate‑speech classification returns the appropriate warning.

---

## TestWarningFST 4 – Sex state maps to sexual-content warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Sex"`

**Expected Output:**  
`"this post may contain sexual content"`

**Description:**  
Validates mapping for sexual‑content classification.

---

## TestWarningFST 5 – Harassment state maps to harassment warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Harass"`

**Expected Output:**  
`"this post may contain harassment"`

**Description:**  
Checks mapping for harassment classification.

---

## TestWarningFST 6 – Self-harm state maps to self-harm warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_SelfHarm"`

**Expected Output:**  
`"this post may contain self-harm"`

**Description:**  
Verifies mapping for self‑harm classification.

---

## TestWarningFST 7 – Threats state maps to threats warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Threats"`

**Expected Output:**  
`"this post may contain threats"`

**Description:**  
Checks mapping for explicit threats classification.

---

## TestWarningFST 8 – Violence state maps to violence warning
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Violence"`

**Expected Output:**  
`"this post may contain violence"`

**Description:**  
Ensures mapping for general violence classification.

---

# Special cases

## TestWarningFST 9 – Safe state returns None
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qF_Safe"`

**Expected Output:**  
`None`

**Description:**  
Confirms that safe content yields no warning string.

---

## TestWarningFST 10 – Unknown state returns None
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qXYZ"`

**Expected Output:**  
`None`

**Description:**  
Unrecognized state identifiers should not produce a warning.

---

## TestWarningFST 11 – Empty string returns None
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`""`

**Expected Output:**  
`None`

**Description:**  
Empty input for the state results in no warning.

---

## TestWarningFST 12 – None input returns None
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`None`

**Expected Output:**  
`None`

**Description:**  
Null input is handled gracefully with no warning.

---

# Input sequence behavior

## TestWarningFST 13 – Sequence of valid and safe states
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`["qSpam", "qF_Sex", "qF_Safe"]`

**Expected Output:**  
`["this post may contain spam", "this post may contain sexual content", None]`

**Description:**  
Validates consistent mapping across multiple successive calls, including a safe case.

---

# Robustness

## TestWarningFST 14 – Case sensitivity (lowercase should fail)
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"qspam"`

**Expected Output:**  
`None`

**Description:**  
The FST expects exact state names; mismatched case must return `None`.

---

## TestWarningFST 15 – Extremely long invalid state returns None
**SetUp:**  
`fst = WarningFST()`

**Input:**  
`"q" + "X" * 1000`

**Expected Output:**  
`None`

**Description:**  
Stress test ensuring long invalid identifiers do not break mapping and return `None`.

---

*End of document.*
