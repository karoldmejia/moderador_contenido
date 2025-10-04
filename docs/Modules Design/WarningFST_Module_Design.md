# WarningFST — Module Design Document
**File:** `warning_fst.py`  
**Date:** 2025-10-03  
**Language:** Python 3.8+  
**Status:** Stable

---

## 1. Abstract
`WarningFST` produces **end-user warning messages** from **final states** emitted by upstream classifiers (e.g., `SpamDFA`, `ContentDFA`, `DirectionalityDFA`). It is intentionally simple: a fixed, explicit mapping from a terminal state string (such as `qF_Hate`) to a short English notice (such as “this post may contain hate speech”). If the input state is unknown, no warning is returned.

This module performs **no text analysis**. It exists to **decouple** user-facing text from classifier internals so that messaging can evolve without changing core classification logic.

---

## 2. Scope and Non‑Goals
**In scope**
- Map a terminal DFA state (string) to a localized warning phrase.
- Return `None` when no message is applicable or the state is unknown.
- Provide a small, dependency‑free component with deterministic behavior.

**Out of scope**
- Detecting content or deciding the final state (handled upstream).
- Severity scoring, multi‑label aggregation, or UI rendering.
- Telemetry, logging, or rate limiting.

---

## 3. Glossary
- **Final state**: A terminal label returned by upstream automata, e.g., `qSpam`, `qF_Offensive`, `qF_Hate`.
- **Warning message**: Short, human‑readable string shown to end users when a final state warrants caution.
- **Localization**: The process of providing warning texts in languages other than English.

---

## 4. External Dependencies and Artifacts
- **Standard library**: none beyond Python built‑ins.
- **Inputs**: state strings produced by upstream modules.
- **Outputs**: warning message strings in English (default), or `None`.

---

## 5. Public API
### 5.1 Class: `WarningFST`
**Intent:** Translate final classifier states into user‑visible warning messages.

**Constructor**
```python
WarningFST()
```
- Initializes an internal mapping `self.transitions: dict[str, str]` from state names to message texts.

**Primary Method (Main Function)**
```python
generate_warning(self, final_state: str) -> str | None
```
- **Role:** Return the warning message associated with `final_state`, or `None` when the state is unrecognized or does not require a warning.
- **Determinism:** For the same `final_state`, the same output is always produced.
- **Side effects:** None.

---

## 6. Mapping (Default English Messages)
| Final state | Warning message |
|---|---|
| `qSpam` | this post may contain spam |
| `qF_Offensive` | this post may contain offensive language |
| `qF_Hate` | this post may contain hate speech |
| `qF_Sex` | this post may contain sexual content |
| `qF_Harass` | this post may contain harassment |
| `qF_SelfHarm` | this post may contain self-harm |
| `qF_Threats` | this post may contain threats |
| `qF_Violence` | this post may contain violence |

> Final states like `qF_Safe` intentionally **do not** produce a warning and should result in `None`.

---

## 7. Algorithm and Control Flow
```text
generate_warning(final_state):
  return transitions.get(final_state, None)
```
- Hash map lookup in O(1) expected time.
- No normalization is performed in the current implementation; the caller must pass canonical state strings.

---

## 8. Correctness and Design Rationale
- **Explicit mapping:** A fixed dictionary ensures clarity during reviews and audits; there is no hidden logic.
- **Determinism:** The same input always yields the same output.
- **Separation of concerns:** Decouples message strings from detection logic, allowing teams to iterate on wording, localization, and policy without touching classifiers.
- **Safety by default:** Unknown states do not trigger warnings (`None`), avoiding accidental over‑labeling.

---

## 9. Interfaces and Contracts
### Inputs
- `final_state: str` — terminal label emitted by upstream modules.

### Outputs
- `str` — warning message in English, or `None` if there is no applicable warning.

### Error Handling
- No exceptions are raised for unknown states; `None` is returned.

### Thread Safety
- Stateless after construction; safe for concurrent reads. If the mapping is modified at runtime, ensure callers coordinate writes.

---

## 10. Test Plan
### 10.1 Unit Tests (pytest)
| ID | Scenario | Input | Expected |
|---|---|---|---|
| T1 | Spam | `"qSpam"` | `"this post may contain spam"` |
| T2 | Offensive | `"qF_Offensive"` | `"this post may contain offensive language"` |
| T3 | Hate | `"qF_Hate"` | `"this post may contain hate speech"` |
| T4 | Sex | `"qF_Sex"` | `"this post may contain sexual content"` |
| T5 | Harassment | `"qF_Harass"` | `"this post may contain harassment"` |
| T6 | Self-harm | `"qF_SelfHarm"` | `"this post may contain self-harm"` |
| T7 | Threats | `"qF_Threats"` | `"this post may contain threats"` |
| T8 | Violence | `"qF_Violence"` | `"this post may contain violence"` |
| T9 | Safe | `"qF_Safe"` | `None` |
| T10 | Unknown | `"qF_Unknown"` | `None` |

### 10.2 Property-Based Checks (optional)
- **Idempotence:** Repeated calls with the same `final_state` yield the same string or `None`.
- **Domain completeness:** Every known final state listed in upstream modules is covered by the mapping; assert set inclusion during CI.

---
