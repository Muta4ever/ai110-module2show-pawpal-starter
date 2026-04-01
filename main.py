"""Demo script: creates sample data and prints Today's Schedule."""
from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def print_schedule(plan: list[Task], owner_name: str) -> None:
    print(f"\n{'='*40}")
    print(f"  Today's Schedule for {owner_name}")
    print(f"{'='*40}")
    if not plan:
        print("  No tasks fit within the available time.")
    for i, task in enumerate(plan, start=1):
        status = "[done]" if task.is_completed() else "[ ]"
        print(f"  {i}. {status} {task.title:<20} {task.duration_minutes:>3} min  ({task.priority.value})")
    total = sum(t.duration_minutes for t in plan)
    print(f"{'-'*40}")
    print(f"  Total: {total} min")
    print(f"{'='*40}\n")


def main() -> None:
    # --- Build the data model ---
    owner = Owner(name="Jordan", daily_available_minutes=60)

    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Luna", species="cat")

    owner.add_pet(dog)
    owner.add_pet(cat)

    # Rex's tasks
    dog.add_task(Task("Morning walk",      30, Priority.HIGH))
    dog.add_task(Task("Training session",  20, Priority.MEDIUM))
    dog.add_task(Task("Bath time",         45, Priority.LOW))

    # Luna's tasks
    cat.add_task(Task("Feed Luna",         10, Priority.HIGH))
    cat.add_task(Task("Litter box clean",  15, Priority.MEDIUM))

    # --- Schedule ---
    scheduler = Scheduler()
    scheduler.load_from_owner(owner)
    plan = scheduler.produce_plan()

    print_schedule(plan, owner.name)


if __name__ == "__main__":
    main()
