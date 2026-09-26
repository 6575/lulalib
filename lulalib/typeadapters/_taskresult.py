from typing import Any

import lulalib.abc
import lulalib.models
import lulalib.observers

class TaskResultType(lulalib.abc.ITypeAdapter[lulalib.models.TaskResult]):

    def __init__(self, ob: lulalib.observers.TaskResultObserver):
        self._ob = ob

    def deserialize(self, data: bytes) -> lulalib.models.TaskResult[Any]:
        return self._ob.task_result_from_buffer(data)

    def serialize(self, data: lulalib.models.TaskResult) -> bytes:
        return bytes(data)

