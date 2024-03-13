from dataclasses import dataclass


@dataclass
class Task:
    id: int
    data: bytes


@dataclass
class Result:
    task_id: int
    success: bool
    data: bytes
