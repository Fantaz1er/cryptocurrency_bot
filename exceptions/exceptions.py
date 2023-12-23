# -*- coding: utf-8 -*-
from typing import Optional

__all__ = ["StopMainTaskError", "StopJobError", "RunMainTaskError", "DeleteUserError"]


class StopMainTaskError(Exception):
    def __init__(self, msg: Optional[str]):
        super().__init__(self)
        self._msg = msg

    def __repr__(self):
        return self._msg if self._msg else "Some errors in stop of the main task"


class StopJobError(Exception):
    def __init__(self, msg: Optional[str]):
        super().__init__(self)
        self._msg = msg

    def __repr__(self):
        return self._msg if self._msg else "Some errors in stop of the job"


class RunMainTaskError(Exception):
    def __init__(self, msg: Optional[str]):
        super().__init__(self)
        self._msg = msg

    def __repr__(self):
        return self._msg if self._msg else "Some errors in run of the math task"


class DeleteUserError(Exception):
    def __init__(self, msg: Optional[str]):
        super().__init__(self)
        self._msg = msg

    def __repr__(self):
        return self._msg if self._msg else ""
