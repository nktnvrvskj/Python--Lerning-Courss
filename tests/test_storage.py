"""Тесты StorageManager (без GUI)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from storage_manager import StorageError, StorageManager  # noqa: E402
from task import Task  # noqa: E402


class StorageManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tasks.json"
        self.storage = StorageManager(self.path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_creates_file_on_first_run(self) -> None:
        self.assertTrue(self.path.exists())
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), [])

    def test_add_assigns_ids_and_persists(self) -> None:
        first = self.storage.add(Task(title="Первая"))
        second = self.storage.add(Task(title="Вторая"))

        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)

        reloaded = StorageManager(self.path).load()
        self.assertEqual([task.title for task in reloaded], ["Первая", "Вторая"])
        self.assertEqual([task.id for task in reloaded], [1, 2])

    def test_update_changes_task(self) -> None:
        task = self.storage.add(Task(title="Черновик"))
        edited = Task(title="Готово", description="Текст", author="Аня", id=task.id)

        self.storage.update(task.id, edited)

        reloaded = StorageManager(self.path).load()[0]
        self.assertEqual(reloaded.title, "Готово")
        self.assertEqual(reloaded.description, "Текст")
        self.assertEqual(reloaded.id, task.id)

    def test_update_unknown_id_raises(self) -> None:
        with self.assertRaises(StorageError):
            self.storage.update(999, Task(title="Нет такой"))

    def test_delete_removes_task(self) -> None:
        task = self.storage.add(Task(title="Удалить меня"))

        self.assertTrue(self.storage.delete(task.id))
        self.assertFalse(self.storage.delete(task.id))
        self.assertEqual(StorageManager(self.path).load(), [])

    def test_legacy_format_is_migrated(self) -> None:
        self.path.write_text(
            json.dumps([{"name": "Задача из v0.1.0"}], ensure_ascii=False),
            encoding="utf-8",
        )

        tasks = StorageManager(self.path).load()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Задача из v0.1.0")
        self.assertIsNotNone(tasks[0].id)

        # после миграции файл уже в новом формате
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(raw[0]["title"], "Задача из v0.1.0")

    def test_plain_strings_from_v010_are_migrated(self) -> None:
        self.path.write_text(
            json.dumps(["Купить хлеб", "Позвонить маме"], ensure_ascii=False),
            encoding="utf-8",
        )

        tasks = StorageManager(self.path).load()

        self.assertEqual(
            [task.title for task in tasks], ["Купить хлеб", "Позвонить маме"]
        )

    def test_broken_json_is_backed_up(self) -> None:
        self.path.write_text("{это не json", encoding="utf-8")

        tasks = StorageManager(self.path).load()

        self.assertEqual(tasks, [])
        self.assertTrue(self.path.with_name("tasks.json.broken").exists())
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), [])

    def test_broken_records_are_skipped(self) -> None:
        self.path.write_text(
            json.dumps(
                [
                    {"title": "Нормальная"},
                    {"description": "без названия"},
                    {"name": "Старая"},
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        tasks = StorageManager(self.path).load()

        self.assertEqual([task.title for task in tasks], ["Нормальная", "Старая"])

    def test_missing_and_duplicate_ids_are_fixed(self) -> None:
        self.path.write_text(
            json.dumps(
                [
                    {"id": 5, "title": "Пять"},
                    {"title": "Без id"},
                    {"id": 5, "title": "Дубль"},
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        tasks = StorageManager(self.path).load()
        ids = [task.id for task in tasks]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(None, ids)


if __name__ == "__main__":
    unittest.main()
