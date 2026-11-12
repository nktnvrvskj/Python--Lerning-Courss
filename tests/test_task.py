"""Тесты модели Task."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from task import Task  # noqa: E402


class TaskTests(unittest.TestCase):
    def test_to_dict_contains_all_fields(self) -> None:
        task = Task(title="Купить хлеб", description="Белый", author="Аня", id=7)
        data = task.to_dict()

        self.assertEqual(
            set(data),
            {"id", "title", "description", "status", "author", "created_at"},
        )
        self.assertEqual(data["id"], 7)
        self.assertEqual(data["title"], "Купить хлеб")
        self.assertFalse(data["status"])

    def test_from_dict_roundtrip(self) -> None:
        original = Task(title="Учёба", description="OOP", author="Иван", id=3)
        restored = Task.from_dict(original.to_dict())

        self.assertEqual(restored.to_dict(), original.to_dict())

    def test_legacy_name_field_is_supported(self) -> None:
        task = Task.from_dict({"name": "Старая задача"})

        self.assertEqual(task.title, "Старая задача")
        self.assertIsNone(task.id)

    def test_empty_title_raises(self) -> None:
        with self.assertRaises(ValueError):
            Task(title="   ")

    def test_toggle_changes_status(self) -> None:
        task = Task(title="Проверка")

        self.assertTrue(task.toggle())
        self.assertTrue(task.status)
        self.assertFalse(task.toggle())

    def test_id_from_string_is_normalized(self) -> None:
        task = Task.from_dict({"id": "12", "title": "Задача"})

        self.assertEqual(task.id, 12)

    def test_string_status_is_parsed(self) -> None:
        self.assertTrue(Task.from_dict({"title": "a", "status": "выполнено"}).status)
        self.assertFalse(Task.from_dict({"title": "a", "status": "нет"}).status)


if __name__ == "__main__":
    unittest.main()
