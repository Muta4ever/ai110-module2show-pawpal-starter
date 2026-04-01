# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

The suite covers 21 tests across five areas:

| Area | What's tested |
|---|---|
| Task basics | `mark_complete()` flips status; `is_completed()` defaults to False |
| Owner / Pet wiring | `add_pet()` sets bidirectional link; removing a pet clears the reference; pet with no tasks returns empty plan |
| `produce_plan()` | Priority ordering (HIGH → MEDIUM → LOW); time budget respected; completed tasks excluded; empty result when nothing fits |
| Sorting | `sort_by_time()` returns tasks chronologically; untimed tasks sorted to the end |
| Recurrence | `next_occurrence()` on a daily/weekly task returns a fresh incomplete copy; one-off tasks return None; start_time is preserved |
| Conflict detection | Overlapping time windows flagged; adjacent (non-overlapping) tasks pass; tasks without `start_time` ignored |

**Confidence level: ★★★★☆**
Core scheduling logic and all named behaviors are covered. The remaining gap is integration-level testing (UI + session state) and date arithmetic for recurring tasks (next_occurrence currently preserves the same time slot but does not advance the calendar date).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
