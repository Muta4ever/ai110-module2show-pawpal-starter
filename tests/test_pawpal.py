from pawpal_system import Task, Pet, Owner, Scheduler, Priority


# ── Required tests ────────────────────────────────────────────────────────────

def test_mark_complete():
    task = Task(title="Walk", duration_minutes=20, priority=Priority.HIGH)
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Feed", duration_minutes=10, priority=Priority.MEDIUM))
    assert len(pet.tasks) == 1


# ── Task basics ───────────────────────────────────────────────────────────────

def test_is_completed_returns_false_before_complete():
    task = Task(title="Groom", duration_minutes=15)
    assert task.is_completed() == False


# ── Owner / Pet wiring ────────────────────────────────────────────────────────

def test_add_pet_sets_owner():
    owner = Owner(name="Alex", daily_available_minutes=60)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    assert pet.owner is owner
    assert pet in owner.pets


def test_pet_with_no_tasks_does_not_affect_plan():
    """Edge case: a pet with zero tasks should produce an empty plan."""
    owner = Owner(name="Sam", daily_available_minutes=60)
    owner.add_pet(Pet(name="Empty", species="cat"))
    s = Scheduler()
    s.load_from_owner(owner)
    assert s.produce_plan() == []


def test_remove_pet_clears_owner_reference():
    owner = Owner(name="Alex", daily_available_minutes=60)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    owner.remove_pet(pet)
    assert pet not in owner.pets
    assert pet.owner is None


# ── produce_plan ──────────────────────────────────────────────────────────────

def test_produce_plan_sorted_high_first():
    low  = Task("Bath",  10, Priority.LOW)
    high = Task("Walk",  10, Priority.HIGH)
    med  = Task("Feed",  10, Priority.MEDIUM)
    s = Scheduler(tasks=[low, high, med], available_minutes=30)
    assert s.produce_plan() == [high, med, low]


def test_produce_plan_respects_time_budget():
    small = Task("Feed", 10, Priority.HIGH)
    big   = Task("Bath", 50, Priority.HIGH)
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


def test_produce_plan_empty_when_no_tasks_fit():
    """Edge case: every task exceeds the budget."""
    big = Task("Bath", 90, Priority.HIGH)
    s = Scheduler(tasks=[big], available_minutes=30)
    assert s.produce_plan() == []


# ── Sorting by time ───────────────────────────────────────────────────────────

def test_sort_by_time_chronological():
    t1 = Task("Evening walk",  20, start_time="18:00")
    t2 = Task("Morning feed",  10, start_time="08:00")
    t3 = Task("Midday groom",  15, start_time="12:30")
    s = Scheduler(tasks=[t1, t2, t3], available_minutes=60)
    sorted_tasks = s.sort_by_time()
    assert sorted_tasks == [t2, t3, t1]


def test_sort_by_time_untimed_tasks_last():
    timed   = Task("Walk",  20, start_time="09:00")
    untimed = Task("Groom", 15)                      # no start_time
    s = Scheduler(tasks=[untimed, timed], available_minutes=60)
    result = s.sort_by_time()
    assert result[0] is timed
    assert result[1] is untimed


def test_sort_by_time_all_untimed_preserves_order():
    t1 = Task("Feed",  10)
    t2 = Task("Groom", 15)
    s = Scheduler(tasks=[t1, t2], available_minutes=60)
    assert s.sort_by_time() == [t1, t2]


# ── Recurrence ────────────────────────────────────────────────────────────────

def test_next_occurrence_daily_returns_fresh_task():
    task = Task("Morning walk", 30, Priority.HIGH, frequency="daily")
    task.mark_complete()
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.completed == False
    assert next_task.title == "Morning walk"
    assert next_task.frequency == "daily"


def test_next_occurrence_weekly_returns_fresh_task():
    task = Task("Bath time", 45, Priority.LOW, frequency="weekly")
    task.mark_complete()
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.completed == False
    assert next_task.frequency == "weekly"


def test_next_occurrence_one_off_returns_none():
    task = Task("Vet visit", 60, Priority.HIGH)  # no frequency
    task.mark_complete()
    assert task.next_occurrence() is None


def test_next_occurrence_preserves_start_time():
    task = Task("Feed", 10, start_time="08:00", frequency="daily")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.start_time == "08:00"


# ── Conflict detection ────────────────────────────────────────────────────────

def test_check_conflicts_detects_overlap():
    walk = Task("Walk", 30, Priority.HIGH, start_time="09:00")
    feed = Task("Feed", 20, Priority.HIGH, start_time="09:15")
    s = Scheduler(tasks=[walk, feed], available_minutes=60)
    warnings = s.check_conflicts([walk, feed])
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]


def test_check_conflicts_no_overlap():
    # walk ends at 09:30 exactly; feed starts at 09:30 — adjacent, not overlapping
    walk = Task("Walk", 30, Priority.HIGH, start_time="09:00")
    feed = Task("Feed", 10, Priority.HIGH, start_time="09:30")
    s = Scheduler(tasks=[walk, feed], available_minutes=60)
    assert s.check_conflicts([walk, feed]) == []


def test_check_conflicts_ignores_tasks_without_start_time():
    t1 = Task("Walk", 30, Priority.HIGH)
    t2 = Task("Feed", 10, Priority.HIGH)
    s = Scheduler(tasks=[t1, t2], available_minutes=60)
    assert s.check_conflicts([t1, t2]) == []


def test_check_conflicts_same_start_time_is_conflict():
    t1 = Task("Walk", 20, start_time="10:00")
    t2 = Task("Feed", 10, start_time="10:00")
    s = Scheduler(tasks=[t1, t2], available_minutes=60)
    assert len(s.check_conflicts([t1, t2])) == 1
