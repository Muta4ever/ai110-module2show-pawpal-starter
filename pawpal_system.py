"""PawPal+ system classes (skeletons).

Generated from UML: Owner, Pet, Task (dataclasses) and Scheduler (regular class).
Method bodies are intentionally left as stubs with docstrings only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


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


@dataclass
class Task:
	"""Represents a single care task for a pet.

	Attributes:
		title: Short description of the task.
		duration_minutes: How long the task takes in minutes.
		priority: Priority level for scheduling decisions.
		completed: Whether the task has been completed.
	"""

	title: str
	duration_minutes: int
	priority: Priority = Priority.MEDIUM
	completed: bool = False

	def mark_complete(self) -> None:
		"""Mark this task as completed."""
		self.completed = True

	def is_completed(self) -> bool:
		"""Return True if the task has been completed."""
		return self.completed


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
		"""Populate tasks and available_minutes from an Owner and their pets.

		Args:
			owner: Owner whose pets' tasks should be loaded.
		"""
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

	def add_task(self, t: Task) -> None:
		"""Add a task to the scheduler's task pool."""
		self.tasks.append(t)

	def remove_task(self, t: Task) -> None:
		"""Remove a task from the scheduler's task pool."""
		self.tasks.remove(t)

	def clear_tasks(self) -> None:
		"""Remove all tasks from the scheduler."""
		self.tasks.clear()
