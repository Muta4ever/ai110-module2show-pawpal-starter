import os
import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

DATA_FILE = "data.json"

PRIORITY_EMOJI = {
    "high":   "🔴 high",
    "medium": "🟡 medium",
    "low":    "🟢 low",
}

# ── Session state: owner persists across reruns; auto-load from disk ─────────
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except Exception:
            st.session_state.owner = None
    else:
        st.session_state.owner = None


def save() -> None:
    """Persist current owner to data.json."""
    if st.session_state.owner is not None:
        st.session_state.owner.save_to_json(DATA_FILE)


st.title("🐾 PawPal+")
st.caption("A pet care planning assistant.")

# ── 1. Owner setup ────────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value=st.session_state.owner.name if st.session_state.owner else "Jordan")
with col2:
    available_mins = st.number_input(
        "Daily available minutes",
        min_value=5, max_value=480,
        value=st.session_state.owner.daily_available_minutes if st.session_state.owner else 60,
    )

if st.button("Set owner"):
    st.session_state.owner = Owner(
        name=owner_name, daily_available_minutes=int(available_mins)
    )
    save()
    st.success(f"Owner set: {owner_name} ({available_mins} min/day)")

if st.session_state.owner is None:
    st.info("Set your owner profile above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ── 2. Pets ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Pets")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Rex")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    st.write("")
    if st.button("Add pet"):
        owner.add_pet(Pet(name=pet_name, species=species))
        save()
        st.success(f"Added {pet_name}!")

if owner.pets:
    for pet in owner.pets:
        st.write(f"- **{pet.name}** ({pet.species}) — {len(pet.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

# ── 3. Tasks ──────────────────────────────────────────────────────────────────
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

    col5, col6 = st.columns(2)
    with col5:
        start_time_input = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 09:00")
    with col6:
        frequency_str = st.selectbox("Frequency", ["one-off", "daily", "weekly"])

    if st.button("Add task"):
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        start_time = start_time_input.strip() if start_time_input.strip() else None
        frequency = None if frequency_str == "one-off" else frequency_str
        target_pet.add_task(Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority(priority_str),
            start_time=start_time,
            frequency=frequency,
        ))
        save()
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # Task table with priority emoji
    rows = [
        {
            "Pet": pet.name,
            "Task": t.title,
            "Duration (min)": t.duration_minutes,
            "Priority": PRIORITY_EMOJI.get(t.priority.value, t.priority.value),
            "Start time": t.start_time or "—",
            "Frequency": t.frequency or "one-off",
            "Done": "✓" if t.is_completed() else "",
        }
        for pet in owner.pets
        for t in pet.tasks
    ]
    if rows:
        st.table(rows)

        # Sorted-by-time expander
        scheduler_preview = Scheduler()
        scheduler_preview.load_from_owner(owner)
        timed = [t for t in scheduler_preview.sort_by_time() if t.start_time]
        if timed:
            with st.expander("View tasks sorted by start time"):
                for t in scheduler_preview.sort_by_time():
                    label = t.start_time if t.start_time else "unscheduled"
                    emoji = PRIORITY_EMOJI.get(t.priority.value, "")
                    st.markdown(f"- **{t.title}** · {label} · {t.duration_minutes} min · {emoji}")
    else:
        st.info("No tasks yet.")

# ── 4. Find next available slot ───────────────────────────────────────────────
st.divider()
st.subheader("Find Next Available Slot")
st.caption("Find the first free time window that fits a task of a given length.")

col1, col2 = st.columns(2)
with col1:
    slot_duration = st.number_input("Task duration (min)", min_value=1, max_value=240, value=30, key="slot_dur")
with col2:
    slot_start_after = st.text_input("Search from (HH:MM)", value="08:00", key="slot_start")

if st.button("Find slot"):
    s = Scheduler()
    s.load_from_owner(owner)
    result = s.find_next_slot(duration=int(slot_duration), start_after=slot_start_after)
    if result:
        st.success(f"Next free {slot_duration}-minute slot starts at **{result}**")
    else:
        st.warning("No free slot found before 22:00 for that duration.")

# ── 5. Generate schedule ──────────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    scheduler.load_from_owner(owner)
    plan = scheduler.produce_plan()

    if not plan:
        st.warning("No tasks fit within your available time, or no tasks have been added.")
    else:
        total = sum(t.duration_minutes for t in plan)
        skipped = len(owner.get_all_tasks()) - len(plan)
        st.success(
            f"Scheduled **{len(plan)} task(s)** — "
            f"{total} of {owner.daily_available_minutes} min used"
            + (f" · {skipped} skipped (over budget or already done)" if skipped else "")
        )

        for i, task in enumerate(plan, 1):
            time_label = f" @ {task.start_time}" if task.start_time else ""
            freq_label = f" · _{task.frequency}_" if task.frequency else ""
            emoji = PRIORITY_EMOJI.get(task.priority.value, "")
            st.markdown(
                f"**{i}. {task.title}**{time_label} — "
                f"{task.duration_minutes} min · {emoji}{freq_label}"
            )

        warnings = scheduler.check_conflicts(plan)
        if warnings:
            st.divider()
            st.markdown("**⚠️ Scheduling conflicts detected:**")
            for w in warnings:
                st.warning(w)
            st.caption(
                "Tip: use 'Find Next Available Slot' above to get a free time window, "
                "then update the conflicting task's start time."
            )
