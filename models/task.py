"""Task: 1 đơn vị công việc cần crawl (chưa có nội dung, chỉ là 'cần làm gì')."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Task:
    """frozen=True -> immutable + tự động hashable, dùng được làm dict key / set member.

    Muốn tăng retries thì tạo bản mới bằng dataclasses.replace(task, retries=task.retries + 1),
    không sửa trực tiếp vì object đã bị "đóng băng".
    """

    url: str
    depth: int = 0
    priority: int = 0
    parent_url: Optional[str] = None
    retries: int = 0
