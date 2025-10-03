

# Moderation FSTs: Censorship & Warning

This file defines two finite-state transducers used in the moderation pipeline:

- Length-Preserving Censorship FST — masks only disallowed tokens (badword, sexword, violence) by replacing each character with * while preserving length; echoes all other tokens; boundary-aware; streaming O(n) time / O(1) space.

- Warning Emission FST — given a single upstream category symbol (qSpam, qF_*), emits one fixed warning message and terminates; deterministic and i18n-friendly.

## Inputs / Outputs

- Censorship FST: input = token/character stream with word boundaries; output = same stream with disallowed tokens replaced by *.

- Warning FST: input = exactly one category symbol; output = exactly one warning sentence.

---


# Length‑Preserving Censorship FST 

This document defines a **finite‑state transducer (FST)** that censors disallowed tokens by replacing each character with `*`, **preserving length**, and leaves safe tokens unchanged. It is designed to plug into a tokenized moderation pipeline but can run standalone on a character stream with word boundaries.

---

## 1. Purpose and Design Goals

- **Mask only disallowed tokens** (`badword`, `sexword`, `violence`) and **do not touch** the rest.
- **Preserve visual alignment** by emitting exactly one `*` per character of the masked token.
- **Respect word boundaries** so punctuation and separators are not masked.
- **Run in streaming mode** with **O(n)** time and **O(1)** memory.

---

## 2. Alphabet and Interface

**Input alphabet (Σ)**, assuming tokenization into words/punctuation (can also be applied at char level):

- Offensive token classes: `badword`, `sexword`, `violence`.
- Safe tokens, including `politics` and the complement set: `Σ_safe = Σ \ {badword, sexword, violence}`.
- Character stream within an offensive token: `letter` (one unit per visible char).
- Word boundary markers: `end_of_word` (space, punctuation, URL/emoji boundary, etc.).
- End of text: `$`.
- Empty output marker: `ε` (notation only).

**Output alphabet (Γ)**: safe tokens echoed verbatim, `*` for masked characters, `$`.

---

## 3. States

```
Q = { q0, qC, qF }
q0: normal flow (pass‑through for safe tokens)
qC: censoring mode (emit '*' per letter until end_of_word)
qF: final state
```

**Initial state:** `q0`  
**Final states:** `{ qF }`

---


## 4. Formal Definition

```
T = (Q, Σ, Γ, δ, λ, q0, F)
```

- `Q = { q0, qC, qF }`
- `Σ = { badword, sexword, violence, politics } ∪ (Σ_safe) ∪ { letter, end_of_word, $ }`
- `Γ = Σ_safe ∪ { *, $ }` (safe tokens echoed; `*` for masked chars; `$`)
- Transition function `δ`:
  - `δ(q0, offensive_token) = qC`
  - `δ(q0, safe_token) = q0`
  - `δ(qC, letter) = qC`
  - `δ(qC, end_of_word) = q0`
  - `δ(q0, $) = qF`
- Output function `λ`:
  - `λ(q0, offensive_token) = ε`
  - `λ(q0, safe_token) = safe_token`
  - `λ(qC, letter) = *`
  - `λ(qC, end_of_word) = ε`
  - `λ(q0, $) = $`

**Invariants**  
1) Only `{badword, sexword, violence}` are masked.  
2) Masking is **length‑preserving**: for a token of length `k`, output is exactly `k` asterisks.  
3) Safe tokens are **byte‑for‑byte** echoed.  
4) Punctuation and separators are **never** masked and mark `end_of_word`.

---

## 5. Operational Semantics (step‑by‑step)

1) In `q0`, read the next token:
   - If it is in `{badword, sexword, violence}`, move to `qC` and emit `ε` (do not emit the token surface).
   - Otherwise, echo the token (`λ = token`) and stay in `q0`.
2) In `qC`, consume the offensive token as a sequence of `letter` steps, emitting `*` for each.
3) Upon `end_of_word`, move back to `q0` without emitting anything.
4) On `$`, move to `qF` and emit `$`.

This runs online with constant memory: no buffering of the whole input is required.

---

## 6. Edge Cases and How They Resolve

- **Trailing punctuation:** `badword!!!` → `*******!!!` (punctuation is outside the masked token).  
- **Hashtags and mentions:** `#badword` or `@badword` → define whether `#`/`@` belongs to the token. If not, masking yields `#*******` / `@*******`.  
- **Hyphenated tokens:** `bad-word` → either treat as two tokens (`***-****`) or a single token (`********`), depending on tokenizer policy.  
- **Unicode & casing:** normalize for matching (NFC/NFKC, case‑fold) but echo original casing for safe tokens; masking is unaffected.  
- **Offensive emojis:** if policy requires, map them into the offensive class so they enter `qC`. Otherwise they pass through.  
- **Multi‑token phrases:** for phrases across tokens, extend detection with a prefix automaton (e.g., Aho–Corasick) that keeps `qC` active across token boundaries.

---


## 7. Examples

| Input tokens                                       | Output tokens                                   |
|----------------------------------------------------|--------------------------------------------------|
| `You`, `are`, `badword`, `!`, `$`                  | `You`, `are`, `*******`, `!`, `$`               |
| `politics`, `debate`, `$`                          | `politics`, `debate`, `$`                       |
| `sexword`, `.`, `$`                                | `******`, `.`, `$`                               |
| `hello`, `badword`, `sexword`, `!`, `$`            | `hello`, `*******`, `******`, `!`, `$`          |
| `#badword`, `$`                                    | `#*******`, `$`                                  |
| `bad-word`, `$` (hyphen splits)                    | `***-****`, `$`                                  |
| `bad-word`, `$` (hyphen inside token)              | `********`, `$`                                  |
| `violence`, `now`, `!`, `$`                        | `********`, `now`, `!`, `$`                      |
| `neutral`, `.`, `$`                                | `neutral`, `.`, `$`                              |

---

## 8. Integration Point 

- The **DFAs label** content (directionality, category, spam).  
- The **FST transforms** the visible text. Masking is policy‑driven and independent from classification.  
- Only tokens in the configured offensive lists enter `qC`. For other categories (e.g., politics alone), the FST is transparent.

---


# Warning Emission FST (Category → Message)

This finite‑state transducer (FST) emits a single warning string given a **moderation category**. It is a simple, stateless mapping from one input symbol to one output message and then termination.

---

## 1. Purpose and Design Goals

- Convert an upstream category (`qSpam`, `qF_*`) into a **fixed warning**.
- Emit exactly **one** message per post.
- Minimal footprint: O(1) space, O(1) time (one transition).

---

## 2. Alphabet and Interface

**Input alphabet (Σ)**  
```
Σ = { qSpam, qF_Offensive, qF_Hate, qF_Sex, qF_Harass, qF_SelfHarm, qF_Threats, qF_Violence, $ }
```
The upstream classifier must produce exactly **one** category symbol per post.

**Output alphabet (Γ)**  
Fixed strings:
- `'this post may contain spam'`
- `'this post may contain offensive language'`
- `'this post may contain hate speech'`
- `'this post may contain sexual content'`
- `'this post may contain harassment'`
- `'this post may contain self-harm'`
- `'this post may contain threats'`
- `'this post may contain violence'`
and the end symbol `$`.

`ε` denotes empty output (notation only).

---

## 3. States

```
Q = { q0, qF }
q0: start, waits for the category symbol
qF: final, after emitting the warning
```

**Initial state:** `q0`  
**Final states:** `{ qF }`

---

## 4. Formal Definition

```
T = (Q, Σ, Γ, δ, λ, q0, F)
```

- `Q = { q0, qF }`
- `Σ = { qSpam, qF_Offensive, qF_Hate, qF_Sex, qF_Harass, qF_SelfHarm, qF_Threats, qF_Violence, $ }`
- `Γ = { 'this post may contain ...', $ }`
- Transition function `δ`:
  - `δ(q0, s) = qF` for any category `s` in Σ \ { $ }
  - `δ(qF, $) = qF` (optional, to pass end symbol)
- Output function `λ`:
  - `λ(q0, qSpam)      = 'this post may contain spam'`
  - `λ(q0, qF_Offensive) = 'this post may contain offensive language'`
  - `λ(q0, qF_Hate)      = 'this post may contain hate speech'`
  - `λ(q0, qF_Sex)       = 'this post may contain sexual content'`
  - `λ(q0, qF_Harass)    = 'this post may contain harassment'`
  - `λ(q0, qF_SelfHarm)  = 'this post may contain self-harm'`
  - `λ(q0, qF_Threats)   = 'this post may contain threats'`
  - `λ(q0, qF_Violence)  = 'this post may contain violence'`
  - `λ(qF, $)            = $` (optional)

Invariants:
1) Exactly one warning is emitted per input post.  
2) The message is a pure function of the input category.  
3) No other text is altered or generated by this transducer.

---

## 5. Operational Notes

- This FST assumes **one** category symbol is chosen upstream. If multiple categories are possible, resolve them **before** calling this FST (e.g., priority order or concatenated notices).
- Internationalization can be handled by replacing the right‑hand strings with locale‑specific templates.
- If the pipeline does not use `$`, omit the optional `$ / $` loop.

---

## 6. Examples

| Input symbol   | Output message                                   |
|----------------|---------------------------------------------------|
| `qSpam`        | `this post may contain spam`                      |
| `qF_Hate`      | `this post may contain hate speech`               |
| `qF_Sex`       | `this post may contain sexual content`            |
| `qF_SelfHarm`  | `this post may contain self-harm`                 |
| `qF_Threats`   | `this post may contain threats`                   |
| `qF_Violence`  | `this post may contain violence`                  |

---

