"""PawPal+ system classes.

Owner, Pet, Task (dataclasses) and Scheduler (regular class).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


def _time_to_minutes(t: str) -> int:
    """Convert a 'HH:MM' string to total minutes since midnight."""
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _minutes_to_time(m: int) -> str:
    """Convert total minutes since midnight to a 'HH:MM' string."""
    return f"{m // 60:02d}:{m % 60:02d}"


class Priority(Enum):
    """Enumeration for task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Maps Priority → sort key so HIGH tasks come first in produce_plan().
_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


@dataclass
class Owner:
    """Represents a pet owner.

    Attributes:
        name: Owner's display name.
        daily_available_minutes: Number of minutes owner has available per day.
        pets: List of pets owned by this owner.
    """

    name: str
    daily_available_minutes: int
    pets: List["Pet"] = field(default_factory=list)

    def add_pet(self, p: "Pet") -> None:
        """Add a Pet to this owner."""
        self.pets.append(p)
        p.owner = self

    def remove_pet(self, p: "Pet") -> None:
        """Remove a Pet from this owner."""
        self.pets.remove(p)
        if p.owner is self:
            p.owner = None

    def get_available_minutes(self) -> int:
        """Return the owner's daily available minutes."""
        return self.daily_available_minutes

    def set_available_minutes(self, mins: int) -> None:
        """Set the owner's daily available minutes."""
        self.daily_available_minutes = mins

    def get_all_tasks(self) -> List["Task"]:
        """Return every Task across all of this owner's pets."""
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    # ── Serialization ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary of this Owner."""
        return {
            "name": self.name,
            "daily_available_minutes": self.daily_available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Owner":
        """Reconstruct an Owner (and its Pets and Tasks) from a dictionary."""
        owner = cls(name=d["name"], daily_available_minutes=d["daily_available_minutes"])
        for pd in d.get("pets", []):
            owner.add_pet(Pet.from_dict(pd))
        return owner

    def save_to_json(self, path: str) -> None:
        """Persist this Owner to a JSON file at path."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> "Owner":
        """Load and return an Owner from a JSON file at path."""
        with open(path) as f:
            return cls.from_dict(json.load(f))


@dataclass
class Pet:
    """Represents a pet that belongs to an Owner.

    Attributes:
        name: Pet's name.
        species: Species string (e.g., "dog", "cat").
        owner: The Owner instance this pet belongs to.
        tasks: Care tasks assigned to this pet.
    """

    name: str
    species: str
    owner: Optional[Owner] = None
    tasks: List["Task"] = field(default_factory=list)

    def set_owner(self, o: Owner) -> None:
        """Assign the pet to an owner."""
        self.owner = o

    def get_owner(self) -> Optional[Owner]:
        """Return the pet's owner, if any."""
        return self.owner

    def add_task(self, t: "Task") -> None:
        """Add a Task to this pet."""
        self.tasks.append(t)

    def remove_task(self, t: "Task") -> None:
        """Remove a Task from this pet."""
        self.tasks.remove(t)

    # ── Serialization ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary of this Pet (owner excluded)."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Pet":
        """Reconstruct a Pet (and its Tasks) from a dictionary."""
        pet = cls(name=d["name"], species=d["species"])
        for td in d.get("tasks", []):
            pet.tasks.append(Task.from_dict(td))
        return pet


@dataclass
class Task:
    """Represents a single care task for a pet.

    Attributes:
        title: Short description of the task.
        duration_minutes: How long the task takes in minutes.
        priority: Priority level for scheduling decisions.
        completed: Whether the task has been completed.
        start_time: Optional scheduled start time in 'HH:MM' format.
        frequency: Recurrence pattern — 'daily', 'weekly', or None for one-off.
    """

    title: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    completed: bool = False
    start_time: Optional[str] = None
    frequency: Optional[str] = None  # "daily", "weekly", or None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_completed(self) -> bool:
        """Return True if the task has been completed."""
        return self.completed

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh copy of this task for its next recurrence, or None.

        A new Task is returned with the same title, duration, priority,
        start_time, and frequency, but completed=False. Returns None if
        frequency is not set (one-off task).
        """
        if self.frequency is None:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            completed=False,
            start_time=self.start_time,
            frequency=self.frequency,
        )

    # ── Serialization ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary of this Task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.value,
            "completed": self.completed,
            "start_time": self.start_time,
            "frequency": self.frequency,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
        """Reconstruct a Task from a dictionary."""
        return cls(
            title=d["title"],
            duration_minutes=d["duration_minutes"],
            priority=Priority(d["priority"]),
            completed=d.get("completed", False),
            start_time=d.get("start_time"),
            frequency=d.get("frequency"),
        )


class Scheduler:
    """Builds an ordered daily plan from Tasks within a time budget.

    Tasks are sorted HIGH → MEDIUM → LOW priority, then greedily selected
    until available_minutes would be exceeded.
    """

    def __init__(self, tasks: Optional[List[Task]] = None, available_minutes: int = 0) -> None:
        """Initialize the Scheduler.

        Args:
            tasks: Optional initial list of Task objects.
            available_minutes: Minutes available for scheduling.
        """
        self.tasks: List[Task] = list(tasks) if tasks else []
        self.available_minutes: int = available_minutes

    def load_from_owner(self, owner: Owner) -> None:
        """Populate tasks and available_minutes from an Owner and their pets."""
        self.available_minutes = owner.get_available_minutes()
        self.tasks = owner.get_all_tasks()

    def produce_plan(self) -> List[Task]:
        """Return an ordered list of tasks that fit within available_minutes.

        Tasks are sorted high-priority first, then selected greedily until
        the time budget is exhausted. Already-completed tasks are excluded.
        """
        candidates = sorted(
            (t for t in self.tasks if not t.is_completed()),
            key=lambda t: _PRIORITY_ORDER[t.priority],
        )
        plan: List[Task] = []
        remaining = self.available_minutes
        for task in candidates:
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan

    def find_next_slot(self, duration: int, start_after: str = "08:00") -> Optional[str]:
        """Find the first free time slot of at least duration minutes.

        Scans existing timed tasks as occupied intervals and returns the
        earliest gap that fits, starting from start_after. Searching stops
        at 22:00. Tasks without a start_time are ignored.

        Args:
            duration: Required slot length in minutes.
            start_after: Earliest acceptable start time in 'HH:MM' format.

        Returns:
            Start time of the free slot as 'HH:MM', or None if none found.
        """
        occupied = sorted(
            (_time_to_minutes(t.start_time), _time_to_minutes(t.start_time) + t.duration_minutes)
            for t in self.tasks
            if t.start_time is not None
        )
        current = _time_to_minutes(start_after)
        end_of_day = _time_to_minutes("22:00")

        for slot_start, slot_end in occupied:
            if current + duration <= slot_start:
                return _minutes_to_time(current)
            if current < slot_end:
                current = slot_end

        if current + duration <= end_of_day:
            return _minutes_to_time(current)
        return None

    def add_task(self, t: Task) -> None:
        """Add a task to the scheduler's task pool."""
        self.tasks.append(t)

    def remove_task(self, t: Task) -> None:
        """Remove a task from the scheduler's task pool."""
        self.tasks.remove(t)

    def clear_tasks(self) -> None:
        """Remove all tasks from the scheduler."""
        self.tasks.clear()

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by start_time.

        Tasks with a start_time come first (earliest first). Tasks without
        a start_time are appended at the end in their original order.
        """
        timed = sorted(
            (t for t in self.tasks if t.start_time is not None),
            key=lambda t: _time_to_minutes(t.start_time),  # type: ignore[arg-type]
        )
        untimed = [t for t in self.tasks if t.start_time is None]
        return timed + untimed

    def check_conflicts(self, plan: List[Task]) -> List[str]:
        """Return warning strings for any overlapping tasks in plan.

        Only tasks with a start_time set are checked. Two tasks conflict
        when their time windows [start, start + duration) overlap.
        """
        timed = [t for t in plan if t.start_time is not None]
        warnings: List[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]
                a_start = _time_to_minutes(a.start_time)  # type: ignore[arg-type]
                b_start = _time_to_minutes(b.start_time)  # type: ignore[arg-type]
                a_end = a_start + a.duration_minutes
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"CONFLICT: '{a.title}' ({a.start_time}, {a.duration_minutes} min) "
                        f"overlaps '{b.title}' ({b.start_time}, {b.duration_minutes} min)"
                    )
        return warnings
