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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
