# Test Design – DirectionalityDFA

This document describes the test design derived from the provided `pytest` test for `DirectionalityDFA`, using the `RegexTokenizer` to generate tokens. For each parametrized case, we specify the setup, the input text, the expected final state, and a short description of what is validated.

**Fixtures & Helper**
- `tokenizer = RegexTokenizer(<path_to_keywords.json>)`
- `dfa = DirectionalityDFA()`
- `run_analysis(text, tokenizer, dfa)` tokenizes the text, feeds tokens into the DFA via `transition`, then calls `end_of_input()` to produce the final state.

---

## Parametrized cases – Real phrases

### TestDirectionalityDFA 1 – Self-directed sentiment via “myself”
**SetUp:**  
`tokenizer = RegexTokenizer(<path_to_keywords.json>)`  
`dfa = DirectionalityDFA()`

**Input:**  
`"I hate myself"`

**Expected Output:**  
`qF_Self`

**Description:**  
Validates that the presence of a first‑person reflexive/self pronoun (e.g., “myself”) drives the DFA to the Self final state.

---

### TestDirectionalityDFA 2 – Other-directed sentiment via “you”
**SetUp:**  
Same as above.

**Input:**  
`"You are stupid"`

**Expected Output:**  
`qF_Others`

**Description:**  
Ensures second‑person pronouns (e.g., “you”) are detected and the DFA resolves to the Others final state.

---

### TestDirectionalityDFA 3 – Generic sentiment (no pronouns)
**SetUp:**  
Same as above.

**Input:**  
`"This is terrible"`

**Expected Output:**  
`qF_Generic`

**Description:**  
Confirms that the absence of self/other pronouns yields a Generic final state.

---

### TestDirectionalityDFA 4 – Mixed pronouns, prioritizing “you”
**SetUp:**  
Same as above.

**Input:**  
`"We are better than you"`

**Expected Output:**  
`qF_Others`

**Description:**  
Validates correct resolution to Others when a second‑person pronoun (“you”) is present alongside group/other pronouns (e.g., “we”).

---

### TestDirectionalityDFA 5 – Self-directed sentiment via “me”
**SetUp:**  
Same as above.

**Input:**  
`"Nobody loves me"`

**Expected Output:**  
`qF_Self`

**Description:**  
Checks detection of the first‑person object pronoun (“me”) leading to the Self final state, even in negative constructions.

---

### TestDirectionalityDFA 6 – Generic sentiment (no pronouns)
**SetUp:**  
Same as above.

**Input:**  
`"Life sucks"`

**Expected Output:**  
`qF_Generic`

**Description:**  
Assures that sentences lacking explicit self/other pronouns are categorized as Generic.

---

*End of document.*
