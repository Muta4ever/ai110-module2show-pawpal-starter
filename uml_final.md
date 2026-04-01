# PawPal+ — Final Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +int dailyAvailableMinutes
        +List~Pet~ pets
        +add_pet(p: Pet) void
        +remove_pet(p: Pet) void
        +get_available_minutes() int
        +set_available_minutes(mins: int) void
        +get_all_tasks() List~Task~
    }

    class Pet {
        +String name
        +String species
        +Owner owner
        +List~Task~ tasks
        +set_owner(o: Owner) void
        +get_owner() Owner
        +add_task(t: Task) void
        +remove_task(t: Task) void
    }

    class Task {
        +String title
        +int durationMinutes
        +Priority priority
        +bool completed
        +String start_time
        +String frequency
        +mark_complete() void
        +is_completed() bool
        +next_occurrence() Task
    }

    class Scheduler {
        +List~Task~ tasks
        +int availableMinutes
        +Scheduler(tasks: List~Task~, availableMinutes: int)
        +load_from_owner(owner: Owner) void
        +produce_plan() List~Task~
        +sort_by_time() List~Task~
        +check_conflicts(plan: List~Task~) List~String~
        +add_task(t: Task) void
        +remove_task(t: Task) void
        +clear_tasks() void
    }

    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
    }

    %% Relationships
    Owner "1" o-- "*" Pet : owns
    Pet "1" o-- "*" Task : has
    Pet --> Owner : belongs to
    Task --> Priority : uses
    Scheduler ..> Owner : load_from_owner()
    Scheduler o-- "0..*" Task : schedules
```

## Changes from initial UML

| What changed | Why |
|---|---|
| `Pet` gained `tasks` list + `add_task()` / `remove_task()` | Tasks need a home on the pet, not floating globally |
| `Owner` gained `get_all_tasks()` | Clean bridge so Scheduler doesn't walk pet internals directly |
| `Scheduler` gained `load_from_owner()`, `sort_by_time()`, `check_conflicts()` | Phase 3 features: time sorting and conflict detection |
| `Task` gained `start_time`, `frequency`, `next_occurrence()` | Support for clock-based scheduling and daily/weekly recurrence |
| Added `Pet "1" o-- "*" Task` relationship | Reflects the actual ownership added in implementation |
| Added `Scheduler ..> Owner` dependency | Reflects `load_from_owner()` call |
