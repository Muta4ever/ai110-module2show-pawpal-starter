# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
a. Initial design
My initial design includes four classes: Priority (an enum), Owner, Pet, Task, and a Scheduler class.

1. Owner holds the owner's name and how many minutes per day they have available for pet care. It maintains a list of their pets and can add or remove them.

2. Pet holds the pet's name and species, and keeps a reference to its owner. It can be assigned to an owner via set_owner().

3. Task represents a single care activity (such as a walk or feeding). It stores a title, how long it takes in minutes, a priority level (low/medium/high via the Priority enum), and whether it has been completed.

4. Scheduler takes a list of tasks and the owner's available minutes, then produces an ordered daily plan via produce_plan(). It also supports adding, removing, and clearing tasks from the pool.



**b. Design changes**

Yes, the design changed in three meaningful ways during implementation.

First, the original `Pet` class had no `tasks` field. The UML only gave it `name`, `species`, and `owner`. During implementation it became clear that without a task list on Pet, there was no natural home for tasks — they'd have to float in the Scheduler or in a global list, which would make it impossible to ask "what does Rex need today?" The fix was to add `tasks: List[Task]` to Pet with `add_task()` and `remove_task()`, making Pet the clear owner of its own care items.

Second, `Owner` gained a `get_all_tasks()` method that wasn't in the original UML. This method became the bridge between Owner and Scheduler — instead of the Scheduler needing to know how to walk the pet list, it could just call `owner.get_all_tasks()`. This kept the Scheduler decoupled from Owner's internal structure.

Third, `Task` grew two new fields — `start_time` (optional `"HH:MM"` string) and `frequency` (`"daily"`, `"weekly"`, or `None`) — to support conflict detection and recurrence. These weren't in the original design because those features were added in a later phase. The `Scheduler` also gained `sort_by_time()`, `check_conflicts()`, and `load_from_owner()` for the same reason.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: **time** (the owner's `daily_available_minutes` budget) and **task priority** (HIGH / MEDIUM / LOW). Priority was treated as the primary constraint because it ensures the most important pet care happens first — a pet missing a high-priority task (like a feeding) is a worse outcome than a low-priority one being skipped. Time is the hard limit: no plan can exceed the budget regardless of priority.

**b. Tradeoffs**

The scheduler uses a **greedy approach** — it picks tasks in priority order and takes each one if it fits, without rearranging. This means a single large HIGH-priority task can block the time slot for several smaller MEDIUM tasks that would collectively fit. For example, a 45-minute bath (HIGH) could prevent three 10-minute feedings (MEDIUM) from being scheduled, even though the feedings might matter more in practice. This tradeoff is reasonable for PawPal+ because the logic stays simple and predictable — owners can read the output and understand exactly why each task was included or skipped, without needing to reason about complex optimization.

For conflict detection, the scheduler checks for **exact time-window overlaps** using `[start, start + duration)` intervals. It only flags tasks that have an explicit `start_time` set and ignores unscheduled tasks entirely. This means it will miss conflicts between a timed task and an untimed one. The tradeoff is intentional: since most tasks in PawPal+ are duration-based rather than clock-based, flagging every pair of unscheduled tasks would produce false positives. Owners who care about exact timing can set `start_time`; everyone else gets a clean, warning-free plan.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used in two main ways. First, to flesh out the method stubs in `pawpal_system.py` — the skeleton structure and docstrings were already in place from the UML design, so the prompt was specific: keep the structure, implement each method, and make `produce_plan()` sort by priority then greedily fit tasks within the time budget. Second, AI helped wire `app.py` to the logic layer by identifying where the placeholder dict-based tasks needed to be replaced with real `Task` objects and `st.session_state` needed to hold the `Owner` instance across reruns.

The most useful prompts were specific ones that referenced the actual file and named the exact behavior expected (e.g., "produce_plan() should sort HIGH first, then fit tasks without exceeding available_minutes"). Vague prompts like "implement the scheduler" tend to produce generic code that doesn't match the existing structure.

**b. Judgment and verification**

The AI-suggested test for `test_add_task_increases_count` originally used `pet.tasks.append(...)` directly instead of calling `pet.add_task()`. This was accepted in the assignment template, but it doesn't actually test the method — it just tests that a list can be appended to. The fix was to replace it with `pet.add_task(...)` so the test exercises the real code path. Verification was done by running `python3 -m pytest -v` and confirming all 7 tests passed, then manually checking that the test would fail if `add_task()` were broken.

---

## 4. Testing and Verification

**a. What you tested**

The final test suite has 21 tests covering six areas: task completion state, Owner/Pet bidirectional wiring, `produce_plan()` behavior (priority ordering, time budget, completed-task exclusion, empty-budget edge case), `sort_by_time()` correctness (chronological order, untimed tasks last), recurrence (`next_occurrence()` for daily/weekly/one-off, start_time preservation), and conflict detection (overlap detected, adjacent not flagged, same start time, no-start_time tasks ignored).

These tests mattered because scheduling bugs tend to be silent — a greedy algorithm that skips the wrong task won't crash, it'll just produce a subtly wrong plan. Having tests for each behavior made it possible to add features (like `frequency` and `start_time`) without worrying about breaking what already worked.

**b. Confidence**

Confidence: **4 out of 5**. The core scheduling logic is solid and all named behaviors have direct tests. The two gaps are: (1) `next_occurrence()` returns a task with the same `start_time` but does not advance the calendar date using `timedelta` — a real daily task should move to tomorrow, not stay on today's slot; (2) there are no integration tests for the Streamlit UI, so `st.session_state` persistence is only verified manually. Given more time, I'd add date arithmetic to `next_occurrence()` and write a test that simulates a full owner → pet → task → schedule workflow end-to-end.

---

## 5. Reflection

**a. What went well**

The data model design held up well throughout the entire project. Starting with a clear ownership hierarchy — Owner contains Pets, Pets contain Tasks — meant that every later feature (sorting, recurrence, conflict detection) had an obvious place to live. The Scheduler never needed to manage its own task list directly; it could just ask the Owner. That clean separation made each phase additive rather than disruptive.

**b. What you would improve**

Two things. First, `next_occurrence()` should use Python's `datetime.timedelta` to compute the actual next date rather than just returning a copy with the same time slot. Second, `produce_plan()` assigns no start times to the tasks it selects — it returns an ordered list but doesn't stamp each task with a computed `"HH:MM"` based on cumulative duration. Adding that would make conflict detection automatic (every planned task would have a start time), and the UI could show a real timeline rather than a numbered list.

**c. Key takeaway**

The most important thing I learned is that AI is a multiplier on the quality of your thinking, not a replacement for it. When the prompts were vague ("implement the scheduler"), the output was generic and needed heavy editing. When the prompts were precise ("sort HIGH first, greedily fit tasks without exceeding available_minutes, exclude completed tasks"), the output matched the design immediately. The human role in AI-assisted engineering is to have a clear enough mental model to write that second kind of prompt — and to know which suggestions to push back on when they don't fit the structure you've already built.
