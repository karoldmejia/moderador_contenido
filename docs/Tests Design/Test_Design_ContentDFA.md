# Test Design – ContentDFA

This document describes the test design derived from the provided `pytest` test file. For each test function, we specify the setup, the input processed by the DFA, the expected final state, and a short description of the test's intent.

---

# Base cases

## TestContentDFA 1 – Empty input (safe)
**SetUp:**  
Initialize the automaton: `dfa = ContentDFA()`

**Input:**  
`""`

**Expected Output:**  
`dfa.qF_Safe`

**Description:**  
Verifies that an empty string does not trigger any category and is classified as safe content.

---

## TestContentDFA 2 – Only irrelevant tokens (safe)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I went to the park today"`

**Expected Output:**  
`dfa.qF_Safe`

**Description:**  
Confirms that text without sensitive keywords remains in the safe state.

---

# Badwords

## TestContentDFA 3 – Self-directed insult (offensive)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I am such an idiot"`

**Expected Output:**  
`dfa.qF_Offensive`

**Description:**  
Detects insulting language directed at the speaker and marks it as offensive.

---

## TestContentDFA 4 – Generic profanity (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"This app is shit"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Evaluates coarse language applied to a generic subject; the DFA classifies it as hate.

---

## TestContentDFA 5 – Insult toward others (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"You are a fucking idiot"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Validates that insults aimed at another person are classified as hate speech.

---

# Politics

## TestContentDFA 6 – Political disdain in first person (offensive)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I hate politicians"`

**Expected Output:**  
`dfa.qF_Offensive`

**Description:**  
Hate-like wording expressed in first person about “politicians”; the DFA treats it as offensive from the speaker.

---

## TestContentDFA 7 – Generic profanity about politics (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Politics is bullshit"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Classifies coarse language applied to the topic “Politics” as hate.

---

## TestContentDFA 8 – Insulting politicians/third parties (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Those politicians are corrupt assholes"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Insults directed at a political group (third parties) fall under the hate category.

---

# Sexual

## TestContentDFA 9 – Sexual wording toward self (sex)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I am horny af"`

**Expected Output:**  
`dfa.qF_Sex`

**Description:**  
Detects explicit sexual language in a self-referential context and labels it as sexual.

---

## TestContentDFA 10 – Generic sexual wording (sex)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"This movie is so sexy"`

**Expected Output:**  
`dfa.qF_Sex`

**Description:**  
Sexual content applied to a general object/topic should be classified as sexual.

---

## TestContentDFA 11 – Sexual harassment toward others (harass)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I wanna grab your pussy"`

**Expected Output:**  
`dfa.qF_Harass`

**Description:**  
Sexual, invasive language aimed at another person is labeled as harassment.

---

# Violence

## TestContentDFA 12 – Self-directed violence (self-harm)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I want to kill myself"`

**Expected Output:**  
`dfa.qF_SelfHarm`

**Description:**  
Detects intent of self-harm and classifies it accordingly.

---

## TestContentDFA 13 – Generic mention of violence (safe)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Violence is everywhere"`

**Expected Output:**  
`dfa.qF_Safe`

**Description:**  
General mention of violence without intent or target does not trigger a sensitive category.

---

## TestContentDFA 14 – Threat against others (threats)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I will kill you"`

**Expected Output:**  
`dfa.qF_Threats`

**Description:**  
Explicit threat against another person falls under the threats category.

---

# Mixtures

## TestContentDFA 15 – Irrelevant tokens + final insult (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Well you are such a dumb idiot"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Irrelevant words followed by an insult toward another person lead to hate.

---

## TestContentDFA 16 – Irrelevant tokens + final sexual term (sex)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"This song is damn sexy"`

**Expected Output:**  
`dfa.qF_Sex`

**Description:**  
Prior irrelevants do not prevent the final sexual keyword from determining the category.

---

## TestContentDFA 17 – Irrelevant tokens + politics with profanity (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Honestly politics is shit"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Combination of a political topic with profanity results in hate.

---

## TestContentDFA 18 – Irrelevant tokens + idea of harming others (threats)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Sometimes I think about hurting others"`

**Expected Output:**  
`dfa.qF_Threats`

**Description:**  
Expresses an intention to harm others; classified as threats.

---

# Combinations politics + badwords

## TestContentDFA 19 – Politics → insult (self) (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"These politicians are idiots"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Insults applied to “politicians” (third parties) in a political context result in hate.

---

## TestContentDFA 20 – Politics + generic profanity (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Politics is stupid shit"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Political topic with coarse language is classified as hate.

---

## TestContentDFA 21 – Politics + insult toward third parties (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Those politicians are fucking idiots"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Explicit insults aimed at a political group are classified as hate.

---

## TestContentDFA 22 – Insult → politics (self) (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Dumb politicians"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
An insulting qualifier applied to “politicians” leads to hate.

---

## TestContentDFA 23 – Profanity → politics (generic) (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Shitty politics"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Profanity attached to “politics” denotes hate toward the political topic.

---

## TestContentDFA 24 – Explicit insult → politics (others) (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Fucking politicians"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Emphatic coarse language applied to “politicians” is classified as hate.

---

# Combinations politics + violence

## TestContentDFA 25 – Politics → violence (self) (violence)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I want to attack politicians"`

**Expected Output:**  
`dfa.qF_Violence`

**Description:**  
Stated intent to commit violence against politicians (first person); categorized as violence.

---

## TestContentDFA 26 – Politics → generic violence mention (safe)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Violence from politicians is everywhere"`

**Expected Output:**  
`dfa.qF_Safe`

**Description:**  
Descriptive mention of violence linked to politicians without intent or threat remains safe.

---

## TestContentDFA 27 – Politics → violence toward third parties (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"We should kill corrupt politicians"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Incitement to kill a third-party group (politicians) is classified by the DFA as hate.

---

## TestContentDFA 28 – Violence → politics (self) (violence)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"I will kill the politicians"`

**Expected Output:**  
`dfa.qF_Violence`

**Description:**  
Direct first-person threat against politicians; result is violence.

---

## TestContentDFA 29 – Violence → generic politics (safe)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"Violence and politics always mix"`

**Expected Output:**  
`dfa.qF_Safe`

**Description:**  
General statement associating violence and politics without a target/intent is safe.

---

## TestContentDFA 30 – Violence → politics toward others (hate)
**SetUp:**  
`dfa = ContentDFA()`

**Input:**  
`"He wants to kill politicians"`

**Expected Output:**  
`dfa.qF_Hate`

**Description:**  
Describes a third party's intent to kill politicians; the DFA marks it as hate.

---


