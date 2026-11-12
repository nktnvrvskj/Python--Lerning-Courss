"""Сохранение задач в JSON-файл.

StorageManager — единственное место, которое знает, *как* задачи лежат
на диске. Заменить JSON на SQLite можно, не меняя остальной код.
"""
from __future__ import annotations

import json
from pathlib import Path

from task import Task


class StorageError(Exception):
    """Ошибка чтения или записи хранилища."""


class StorageManager:
    """Управляет персистентностью коллекции задач."""

    def __init__(self, path: str | Path = "tasks.json") -> None:
        """Запомнить путь к файлу и загрузить существующие задачи."""
        self.path = Path(path)
        self._tasks: list[Task] = []
        self.load()

    # ---------- чтение / запись ----------
    def load(self) -> list[Task]:
        """Прочитать все задачи из хранилища.

        Битый JSON не роняет приложение: файл сохраняется как резервная
        копия, а работа продолжается с пустым списком.
        """
        self._tasks = []

        if not self.path.exists():
            self.save([])
            return []

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            raise StorageError(f"Не удалось прочитать {self.path}: {exc}") from exc
        except json.JSONDecodeError:
            self._backup_broken_file()
            self.save([])
            return []

        if isinstance(raw, dict):
            raw = raw.get("tasks", [])
        if not isinstance(raw, list):
            raw = []

        next_id = 1
        used_ids: set[int] = set()
        changed = False

        for record in raw:
            try:
                task = Task.from_dict(record)
            except (TypeError, ValueError, AttributeError):
                # Пропускаем повреждённую запись, но не теряем остальные.
                changed = True
                continue

            if task.id is None or task.id in used_ids:
                task.id = next_id
                changed = True

            used_ids.add(task.id)
            next_id = max(next_id, task.id + 1)
            self._tasks.append(task)

        if changed:
            self.save(self._tasks)

        return list(self._tasks)

    def save(self, tasks: list[Task]) -> None:
        """Записать весь список задач в хранилище (атомарно)."""
        self._tasks = list(tasks)
        payload = [task.to_dict() for task in self._tasks]
        tmp_path = self.path.with_name(self.path.name + ".tmp")

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp_path.replace(self.path)
        except OSError as exc:
            raise StorageError(f"Не удалось сохранить {self.path}: {exc}") from exc

    # ---------- CRUD ----------
    def add(self, task: Task) -> Task:
        """Добавить одну задачу и выдать ей уникальный id."""
        if task.id is None or any(item.id == task.id for item in self._tasks):
            task.id = self._next_id()
        self._tasks.append(task)
        self.save(self._tasks)
        return task

    def update(self, task_id: int, task: Task) -> Task:
        """Обновить задачу по id."""
        for index, current in enumerate(self._tasks):
            if current.id == task_id:
                task.id = task_id
                self._tasks[index] = task
                self.save(self._tasks)
                return task
        raise StorageError(f"Задача с id={task_id} не найдена")

    def delete(self, task_id: int) -> bool:
        """Удалить задачу по id. Вернуть True, если задача была найдена."""
        for index, current in enumerate(self._tasks):
            if current.id == task_id:
                del self._tasks[index]
                self.save(self._tasks)
                return True
        return False

    def get(self, task_id: int) -> Task | None:
        """Найти задачу по id или вернуть None."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    # ---------- служебное ----------
    def _next_id(self) -> int:
        """Следующий свободный id (нумерация начинается с 1)."""
        existing = [task.id for task in self._tasks if task.id is not None]
        return max(existing, default=0) + 1

    def _backup_broken_file(self) -> None:
        """Сохранить копию повреждённого файла рядом с оригиналом."""
        backup = self.path.with_name(self.path.name + ".broken")
        try:
            backup.write_bytes(self.path.read_bytes())
        except OSError:
            pass
