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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it. 

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

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
