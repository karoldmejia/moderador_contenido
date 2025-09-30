# Token-by-Token DFA for sensitive content and spam detection

This model is designed to analyze text **token by token** and classify it into categories of sensitive content, spam, or political speech. It integrates rules based on:

* Pronouns and verbs to detect actions directed at oneself or others.
* Sensitive words (violence, sexual content, hate, politics, self-harm).
* Spam detection through repeated URLs, hashtags, or combinations with spamwords/fakeclaims.

---

Before, we would like to explain the different categories which our model can classify content:


### 1.1. Hate speech / Offensive

* **Lists used:** `badwords`, `politics` (when combined with insults), `bademojis`.
* **Description:** Dretection of insults, derogatory expressions, racism, sexism, or direct attacks.
* **Example:**

  ```
  You are a stupid idiot! 💀
  → Tokens: BADWORD, BAD_EMOJI → Category: Hate Speech
  ```

---

### 1.2. Sexual / Harassment

* **Lists used:** `sexwords`, some `badwords`, related emojis.
* **Description:** Detection of explicit sexual references, harassment, or non-consensual sexting.
* **Example:**

  ```
  Wanna see my nudes? 🍆
  → Tokens: SEXWORD, EMOJI → Category: Sexual Content
  ```


### 1.3. Violence / Threats / qF_Self-harm

* **Lists used:** `violence`, `bademojis` (weapons, knives, etc.), `selfharm`, specific hashtags (#endit, #selfharm)
* **Description:** Identification of physical threats, violent expressions, or incitement to harm.
* **Example:**

  ```
  I will kill you 🔪
  → Tokens: VIOLENCE, NEG_EMOJI → Category: Violence / Threat
  ```


### 1.4. Spam

* **Lists used:** `spamwords`, `fakeclaims`, repeated URLs, repeated hashtags.
* **Description:** Identification of fraud attempts, mass advertising, or suspicious links.
* **Example:**

  ```
  Win BIG! Click here to get FREE $$$ http://spam.com
  → Tokens: SPAMWORD, FAKECLAIM, URL → Category: Spam
  ```

### 1.5. Neutral / Safe content

* **Description:** Default category when no problematic patterns are detected.
* **Example:**

  ```
  Having coffee with friends ☕
  → Tokens: WORD, WORD, WORD, EMOJI → Category: Safe
  ```

---

# 1. Classifying offensive content

We decided to work with multiple DFA's, taking in account the differences in non appropriate posts, centering on differences between attack to themselves, attackes to other people or generic inappropriate behavior. For this, we use two dfa's:

1. Directionality DFA: identifies whether the post talks about oneself, others, or is generic.
2. Content classification DFA: receives the directionality as a tag and classifies the content based on the detected keywords.
---

## 1. Directionality DFA

### 1.1 States:

[
Q_1 = {q0, q1, q2, q3, qF_Self, qF_Others, qF_Generic}
]

### 1.2 Alphabet ((\Sigma_1)):

[
\Sigma_1 = {\text{self}, \text{other}, \epsilon, \Sigma, $ }
]

Where:

* `self` = pronoun indicating an action directed at oneself
* `other` = pronoun indicating an action directed at others
* `ε` = empty transition (no pronoun detected)
* `Σ` = any irrelevant symbol/token
* `$` = end of string

### 1.3 Initial state:

[
q_0 = q0
]

### 1.4 Final states:

[
F_1 = {qF_Self, qF_Others, qF_Generic}
]

### 1.5 Transition function ((\delta_1)):

| State | Symbol | Next state |
| ----- | ------ | ---------- |
| q0    | self   | q1         |
| q0    | other  | q2         |
| q0    | ε      | q3         |
| q1    | Σ      | q1         |
| q2    | Σ      | q2         |
| q3    | Σ      | q3         |
| q1    | $      | qF_Self    |
| q2    | $      | qF_Others  |
| q3    | $      | qF_Generic |

---

## 2. Content classification DFA 

This DFA **receives the directionality** as a tag from the previous DFA and classifies the post based on sensitive words.

This automaton is defined as:
[
M = (Q, \Sigma, \delta, q_0, F)
]

---

### 1. States (Q)

[
Q = { q0, qB, qP, qPB, qV, qPV, qS, qF_Offensive, qF_Hate, qF_Sex, qF_Harass, qF_SelfHarm, qF_Threats, qF_Violence, qF_Safe }
]

---

### 2. Alphabet (Σ)

[
\Sigma = { \text{badword}, \text{politics}, \text{sexword}, \text{violence}, Σ, $ + qF_Self, $ + qF_Others, $ + qF_Generic, $ + qF_Self/qF_Generic, $ + qF_Generic/qF_Others }
]

* **badword, politics, sexword, violence**: Keyword tokens.
* **Σ**: Any other irrelevant tokens.
* **$ + qF_Self, $ + qF_Others, $ + qF_Generic, etc.**: Special end-of-string symbols that come from the directionality DFA.

---

### 3. Initial state

[
q_0 = q0
]

---

### 4. Final states (F)

[
F = { qF_Offensive, qF_Hate, qF_Sex, qF_Harass, qF_SelfHarm, qF_Threats, qF_Violence, qF_Safe }
]

---

### 5. Transition function (δ)

[
\delta : Q \times \Sigma \to Q
]

We define it in a table:

| Current state | Input symbol    | Next state   |
| ------------- | --------------- | ------------ |
| q0            | Σ               | q0           |
| q0            | badword         | qB           |
| q0            | politics        | qP           |
| q0            | sexword         | qS           |
| q0            | violence        | qV           |
| q0            | $               | qF_Safe      |
| qB            | politics        | qPB          |
| qB            | Σ               | qB           |
| qB            | $ + qF_Self     | qF_Offensive |
| qB            | $ + qF_Generic  | qF_Offensive |
| qB            | $ + qF_Others   | qF_Hate      |
| qP            | badword         | qPB          |
| qP            | violence        | qPV          |
| qP            | Σ               | qP           |
| qP            | $ + qF_Self     | qF_Offensive |
| qP            | $ + qF_Generic  | qF_Offensive |
| qP            | $ + qF_Others   | qF_Hate      |
| qPB           | Σ               | qPB          |
| qPB           | $ + qF_Self     | qF_Offensive |
| qPB           | $ + qF_Generic  | qF_Offensive |
| qPB           | $ + qF_Others   | qF_Hate      |
| qV            | politics        | qPV          |
| qV            | Σ               | qV           |
| qV            | $ + qF_Self     | qF_SelfHarm  |
| qV            | $ + qF_Generic  | qF_Violence  |
| qV            | $ + qF_Others   | qF_Threats   |
| qPV           | Σ               | qPV          |
| qPV           | $ + qF_Self     | qF_Violence  |
| qPV           | $ + qF_Generic  | qF_Hate      |
| qPV           | $ + qF_Others   | qF_Hate      |
| qS            | Σ               | qS           |
| qS            | $ + qF_Self     | qF_Sex       |
| qS            | $ + qF_Generic  | qF_Sex       |
| qS            | $ + qF_Others   | qF_Harass    |


#### Important notes

* `politics` is safe alone, **unless** it is accompanied by a bad word or violence.
* `violence` is only considered a threat, self-harm, or generic violence.
* `politics + violence` can be **Hate** (if it's directed at others or generic) or **Violence** (if it's directed at oneself).