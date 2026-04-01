import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state: owner persists across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = None

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant.")

# ── 1. Owner setup ──────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Jordan")
with col2:
    available_mins = st.number_input(
        "Daily available minutes", min_value=5, max_value=480, value=60
    )

if st.button("Set owner"):
    st.session_state.owner = Owner(
        name=owner_name, daily_available_minutes=int(available_mins)
    )
    st.success(f"Owner set: {owner_name} ({available_mins} min/day)")

if st.session_state.owner is None:
    st.info("Set your owner profile above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ── 2. Pets ─────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Pets")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Rex")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    st.write("")  # vertical alignment spacer
    if st.button("Add pet"):
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name}!")

if owner.pets:
    for pet in owner.pets:
        st.write(f"- **{pet.name}** ({pet.species}) — {len(pet.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

# ── 3. Tasks ─────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority_str = st.selectbox("Priority", ["high", "medium", "low"])

    if st.button("Add task"):
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority(priority_str),
            )
        )
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # Show all tasks across all pets
    rows = [
        {
            "Pet": pet.name,
            "Task": t.title,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority.value,
            "Done": "✓" if t.is_completed() else "",
        }
        for pet in owner.pets
        for t in pet.tasks
    ]
    if rows:
        st.table(rows)
    else:
        st.info("No tasks yet.")

# ── 4. Generate schedule ─────────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    scheduler.load_from_owner(owner)
    plan = scheduler.produce_plan()

    if not plan:
        st.warning(
            "No tasks fit within your available time, or no tasks have been added."
        )
    else:
        total = sum(t.duration_minutes for t in plan)
        skipped = len(owner.get_all_tasks()) - len(plan)
        st.success(
            f"Scheduled **{len(plan)} task(s)** — "
            f"{total} of {owner.daily_available_minutes} min used"
            + (f" · {skipped} task(s) skipped (over budget or already done)" if skipped else "")
        )
        for i, task in enumerate(plan, 1):
            st.markdown(
                f"**{i}. {task.title}** — {task.duration_minutes} min · "
                f"*{task.priority.value} priority*"
            )
