# Test Design – CensorshipFST

This document describes the test design for the `CensorshipFST` based on the provided `pytest` tests. Each case includes setup, input, expected censored output, and a brief description.

---

## TestCensorshipFST 1 – Empty input returns empty string
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`""`

**Expected Output:**  
`""`

**Description:**  
Validates that empty input is returned unchanged.

---

## TestCensorshipFST 2 – Safe political text remains unchanged
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"The president will speak today"`

**Expected Output:**  
`"The president will speak today"`

**Description:**  
Confirms that non-offensive, non-sexual, non-violent content is not censored.

---

## TestCensorshipFST 3 – Simple badword is masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"You are a stupid person"`

**Expected Output:**  
`"You are a ****** person"`

**Description:**  
Checks that the bad word “stupid” is replaced by six asterisks preserving length.

---

## TestCensorshipFST 4 – Simple sexword is masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"He watched porn last night"`

**Expected Output:**  
`"He watched **** last night"`

**Description:**  
Ensures sexual terms (here “porn”) are censored with length-matched asterisks.

---

## TestCensorshipFST 5 – Simple violence word is masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"They will kill him"`

**Expected Output:**  
`"They will **** him"`

**Description:**  
Verifies violent terms (here “kill”) are censored.

---

## TestCensorshipFST 6 – Multiple badwords are each masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"You are a dumb idiot!"`

**Expected Output:**  
`"You are a **** *****!"`

**Description:**  
Validates multiple offensive words (“dumb”, “idiot”) are independently censored.

---

## TestCensorshipFST 7 – Badword at sentence start is masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"Asshole came to the party"`

**Expected Output:**  
`"******* came to the party"`

**Description:**  
Checks masking when the offensive word is the first token.

---

## TestCensorshipFST 8 – Sexwords in the middle are masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"She likes boobs and sex"`

**Expected Output:**  
`"She likes ***** and ***"`

**Description:**  
Ensures all sexual terms (“boobs”, “sex”) are censored, preserving lengths.

---

## TestCensorshipFST 9 – Violence + badword both masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"The jerk tried to shoot them"`

**Expected Output:**  
`"The **** tried to ***** them"`

**Description:**  
Confirms simultaneous masking for mixed categories (badword “jerk”, violence “shoot”).

---

## TestCensorshipFST 10 – Political nouns alone remain unchanged
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"Liberals and conservatives are debating"`

**Expected Output:**  
`"Liberals and conservatives are debating"`

**Description:**  
Validates that political group names are not censored by this FST.

---

## TestCensorshipFST 11 – Badword with negative emoji retains emoji
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"You are a bastard 💀"`

**Expected Output:**  
`"You are a ******* 💀"`

**Description:**  
Ensures the badword is masked while non-text symbols/emojis are preserved.

---

## TestCensorshipFST 12 – Sexword and badword both masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"That idiot watched porn yesterday"`

**Expected Output:**  
`"That ***** watched **** yesterday"`

**Description:**  
Checks proper masking across categories (“idiot”, “porn”).

---

## TestCensorshipFST 13 – Multiple offensive words in a row masked
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"Dumb moron asshole"`

**Expected Output:**  
`"**** ***** *******"`

**Description:**  
Verifies contiguous offensive words are all censored correctly.

---

## TestCensorshipFST 14 – Mixed safe + offensive masks only the offensive
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"My friend is a jerk"`

**Expected Output:**  
`"My friend is a ****"`

**Description:**  
Ensures only the offensive term is masked while safe text remains.

---

## TestCensorshipFST 15 – Long mixed text masks all targeted categories
**SetUp:**  
`fst = CensorshipFST()`

**Input:**  
`"The stupid jerk tried to kill her while watching porn"`

**Expected Output:**  
`"The ****** **** tried to **** her while watching ****"`

**Description:**  
End-to-end scenario mixing badwords, violence, and sex; all targeted terms are censored with length-preserving asterisks.

