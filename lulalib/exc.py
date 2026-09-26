from __future__ import annotations
from typing import TYPE_CHECKING

from uuid import UUID

if TYPE_CHECKING:
    from lulalib.models.taskresult import TaskResult

class TaskResultRetException(Exception):
    pass

class TaskResultStateError(RuntimeError):
    pass

class TaskAlreadyDoneError(RuntimeError):

    def __init__(self,
                 *args: object,
                 result: TaskResult,
                 task_id: UUID,
                 ) -> None:
        self.result = result
        self.task_id = task_id
        super().__init__(*args)

class TaskDismissedError(RuntimeError):

    def __init__(self, *args, task_id: UUID, reason: str | None = None):
        self.task_id = task_id
        self.reason = reason

class FrozenStateError(RuntimeError):
    pass

class MissingTypeAdapter(Exception):
    pass