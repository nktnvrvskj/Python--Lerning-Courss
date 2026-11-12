"""Модель задачи.

Класс не знает ни про JSON, ни про tkinter: он только хранит данные
и умеет превращаться в словарь и обратно.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

DEFAULT_AUTHOR = "—"


@dataclass
class Task:
    """Одна задача менеджера."""

    title: str
    description: str = ""
    status: bool = False
    author: str = DEFAULT_AUTHOR
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    id: int | None = None

    def __post_init__(self) -> None:
        """Привести поля к ожидаемым типам и проверить обязательные данные."""
        self.title = str(self.title or "").strip()
        if not self.title:
            raise ValueError("Название задачи не может быть пустым")

        self.description = str(self.description or "").strip()
        self.author = str(self.author or "").strip() or DEFAULT_AUTHOR
        self.status = bool(self.status)

        if self.id is not None:
            try:
                self.id = int(self.id)
            except (TypeError, ValueError):
                self.id = None

    def to_dict(self) -> dict:
        """Сериализовать задачу в словарь для StorageManager."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "author": self.author,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Восстановить задачу из словаря.

        Понимает и старый формат v0.1.0 ({"name": "..."}): такие записи
        автоматически превращаются в задачи с названием из поля ``name``.
        """
        if isinstance(data, str):
            data = {"name": data}
        if not isinstance(data, dict):
            raise ValueError("Запись задачи должна быть словарём или строкой")

        title = data.get("title", data.get("name", ""))
        description = data.get("description", "")
        author = data.get("author", DEFAULT_AUTHOR)

        raw_status = data.get("status", False)
        if isinstance(raw_status, str):
            status = raw_status.strip().lower() in {
                "1",
                "true",
                "yes",
                "done",
                "выполнено",
            }
        else:
            status = bool(raw_status)

        created_at = data.get("created_at")
        if not created_at:
            created_at = datetime.now().isoformat(timespec="seconds")

        return cls(
            title=str(title),
            description=str(description),
            status=status,
            author=str(author),
            created_at=str(created_at),
            id=data.get("id"),
        )

    def toggle(self) -> bool:
        """Переключить статус «выполнено» и вернуть новое значение."""
        self.status = not self.status
        return self.status

    def __str__(self) -> str:
        mark = "✓" if self.status else "○"
        return f"{mark} {self.title}"
