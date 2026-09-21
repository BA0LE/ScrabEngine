"""Priority task scheduler used by the engine."""

import heapq
import itertools


class Scheduler:
    """A stable priority queue (lower numeric priority runs first)."""

    def __init__(self):
        self.tasks = []
        self._sequence = itertools.count()
        self.task_finder = {}
        self.REMOVED = "<removed-task>"

    def add_task(self, task, priority=None):
        if priority is None:
            priority = getattr(task, "priority", 0)

        count = next(self._sequence)
        entry = [priority, count, task]

        self.task_finder[task] = entry
        heapq.heappush(self.tasks, entry)

    def is_empty(self):
        return not self.tasks

    def get_next(self):
        if self.is_empty():
            raise IndexError("(C21) cannot get a task from an empty scheduler")
        while self.tasks:
            priority, count, task = heapq.heappop(self.tasks)
            if task is not self.REMOVED:
                del self.task_finder[task]
                return task
        raise IndexError("(C22) cannot get a task from an empty scheduler")

    def remove_task(self, task):
        entry = self.task_finder.pop(task)
        entry[-1] = self.REMOVED

    def __len__(self):
        return len(self.tasks)


scheduler = Scheduler
