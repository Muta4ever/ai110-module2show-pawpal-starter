from pawpal_system import Task, Pet, Owner, Scheduler, Priority


# --- Required tests ---

def test_mark_complete():
    task = Task(title="Walk", duration_minutes=20, priority=Priority.HIGH)
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Feed", duration_minutes=10, priority=Priority.MEDIUM))
    assert len(pet.tasks) == 1


# --- Additional tests ---

def test_is_completed_returns_false_before_complete():
    task = Task(title="Groom", duration_minutes=15)
    assert task.is_completed() == False


def test_add_pet_sets_owner():
    owner = Owner(name="Alex", daily_available_minutes=60)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    assert pet.owner is owner
    assert pet in owner.pets


def test_produce_plan_sorted_high_first():
    low = Task("Bath",  10, Priority.LOW)
    high = Task("Walk", 10, Priority.HIGH)
    med = Task("Feed",  10, Priority.MEDIUM)
    s = Scheduler(tasks=[low, high, med], available_minutes=30)
    plan = s.produce_plan()
    assert plan == [high, med, low]


def test_produce_plan_respects_time_budget():
    small = Task("Feed",  10, Priority.HIGH)
    big   = Task("Bath",  50, Priority.HIGH)
    s = Scheduler(tasks=[small, big], available_minutes=30)
    plan = s.produce_plan()
    assert small in plan
    assert big not in plan


def test_produce_plan_excludes_completed():
    done = Task("Walk", 10, Priority.HIGH)
    done.mark_complete()
    todo = Task("Feed", 10, Priority.MEDIUM)
    s = Scheduler(tasks=[done, todo], available_minutes=60)
    plan = s.produce_plan()
    assert done not in plan
    assert todo in plan


# --- Conflict detection tests ---

def test_check_conflicts_detects_overlap():
    # Walk 09:00 for 30 min ends at 09:30; Feed 09:15 starts inside that window
    walk = Task("Walk", 30, Priority.HIGH, start_time="09:00")
    feed = Task("Feed", 20, Priority.HIGH, start_time="09:15")
    s = Scheduler(tasks=[walk, feed], available_minutes=60)
    warnings = s.check_conflicts([walk, feed])
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]


def test_check_conflicts_no_overlap():
    # Walk 09:00 for 30 min ends exactly at 09:30; Feed starts at 09:30 — no overlap
    walk = Task("Walk", 30, Priority.HIGH, start_time="09:00")
    feed = Task("Feed", 10, Priority.HIGH, start_time="09:30")
    s = Scheduler(tasks=[walk, feed], available_minutes=60)
    warnings = s.check_conflicts([walk, feed])
    assert warnings == []


def test_check_conflicts_ignores_tasks_without_start_time():
    t1 = Task("Walk", 30, Priority.HIGH)          # no start_time
    t2 = Task("Feed", 10, Priority.HIGH)           # no start_time
    s = Scheduler(tasks=[t1, t2], available_minutes=60)
    warnings = s.check_conflicts([t1, t2])
    assert warnings == []
