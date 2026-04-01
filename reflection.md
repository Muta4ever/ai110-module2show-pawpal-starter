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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
