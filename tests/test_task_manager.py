"""Тесты бизнес-логики TaskManager с подставным интерфейсом (без GUI)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from storage_manager import StorageManager  # noqa: E402
from task import Task  # noqa: E402
from task_manager import TaskManager  # noqa: E402


class FakeInterface:
    """Минимальная замена Interface для тестов логики."""

    def __init__(self) -> None:
        self.actions: dict = {}
        self.inputs = {"title": "", "description": "", "author": ""}
        self.shown: list = []
        self.details = None
        self.messages: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.confirm = True
        self.selection: int | None = None
        self.built = False
        self.quit_called = False
        self.run_called = False
        self.focused = False

    def set_actions(self, actions: dict) -> None:
        self.actions = dict(actions)

    def build(self) -> None:
        self.built = True

    def get_input(self) -> dict:
        return dict(self.inputs)

    def set_input(self, data) -> None:
        payload = data.to_dict() if hasattr(data, "to_dict") else dict(data or {})
        self.inputs = {
            "title": payload.get("title", ""),
            "description": payload.get("description", ""),
            "author": payload.get("author", ""),
        }

    def clear_input(self) -> None:
        self.inputs = {"title": "", "description": "", "author": ""}

    def show_tasks(self, tasks: list) -> None:
        self.shown = list(tasks)

    def show_task_details(self, task) -> None:
        self.details = task

    def show_message(self, title: str, text: str) -> None:
        self.messages.append((title, text))

    def show_warning(self, title: str, text: str) -> None:
        self.warnings.append((title, text))

    def ask_confirm(self, title: str, text: str) -> bool:
        return self.confirm

    def get_selected_index(self) -> int | None:
        return self.selection

    def select_index(self, index: int) -> None:
        self.selection = index

    def clear_selection(self) -> None:
        self.selection = None

    def focus_title(self) -> None:
        self.focused = True

    def quit(self) -> None:
        self.quit_called = True

    def run(self) -> None:
        self.run_called = True


class TaskManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tasks.json"
        self.storage = StorageManager(self.path)
        self.ui = FakeInterface()
        self.manager = TaskManager(storage=self.storage, interface=self.ui)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_task(self) -> None:
        self.ui.inputs = {
            "title": "  Написать отчёт ",
            "description": "до пятницы",
            "author": "Аня",
        }

        self.manager.create_task()

        tasks = self.storage.load()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Написать отчёт")
        self.assertEqual(tasks[0].description, "до пятницы")
        self.assertEqual(tasks[0].author, "Аня")
        self.assertEqual(len(self.ui.shown), 1)
        # после создания задача остаётся выбранной, а поля — заполненными
        self.assertEqual(self.ui.inputs["title"], "Написать отчёт")
        self.assertEqual(self.ui.selection, 0)
        self.assertIsNotNone(self.ui.details)
        self.assertEqual(self.ui.details.title, "Написать отчёт")
        self.assertEqual(self.ui.warnings, [])

    def test_create_task_requires_title(self) -> None:
        self.ui.inputs = {"title": "   ", "description": "", "author": ""}

        self.manager.create_task()

        self.assertEqual(self.storage.load(), [])
        self.assertEqual(len(self.ui.warnings), 1)

    def test_edit_requires_selection(self) -> None:
        self.ui.selection = None

        self.manager.edit_task()

        self.assertEqual(len(self.ui.warnings), 1)

    def test_edit_selected_task_preserves_id_status_and_created_at(self) -> None:
        task = self.storage.add(Task(title="Старое", description="old", author="Аня"))
        task.status = True
        self.storage.update(task.id, task)
        self.manager.refresh()
        self.ui.selection = 0
        self.ui.inputs = {"title": "Новое", "description": "new", "author": "Иван"}

        self.manager.edit_task()

        saved = self.storage.get(task.id)
        self.assertEqual(saved.title, "Новое")
        self.assertEqual(saved.description, "new")
        self.assertEqual(saved.author, "Иван")
        self.assertEqual(saved.id, task.id)
        self.assertTrue(saved.status)
        self.assertEqual(saved.created_at, task.created_at)
        self.assertEqual(self.ui.selection, 0)

    def test_toggle_status_persists(self) -> None:
        task = self.storage.add(Task(title="Сделать"))
        self.manager.refresh()
        self.ui.selection = 0

        self.manager.toggle_status()

        self.assertTrue(self.storage.get(task.id).status)
        self.assertIn("выполнена", self.ui.messages[-1][1])

        self.manager.toggle_status()
        self.assertFalse(self.storage.get(task.id).status)

    def test_delete_requires_confirmation(self) -> None:
        task = self.storage.add(Task(title="Удалить"))
        self.manager.refresh()
        self.ui.selection = 0
        self.ui.confirm = False

        self.manager.delete_task()

        self.assertIsNotNone(self.storage.get(task.id))

        self.ui.confirm = True
        self.manager.delete_task()

        self.assertIsNone(self.storage.get(task.id))
        self.assertEqual(self.storage.load(), [])

    def test_select_task_fills_form(self) -> None:
        self.storage.add(Task(title="Выбрать", description="описание", author="Аня"))
        self.manager.refresh()
        self.ui.selection = 0

        self.manager.select_task()

        self.assertEqual(self.ui.inputs["title"], "Выбрать")
        self.assertEqual(self.ui.inputs["description"], "описание")
        self.assertIsNotNone(self.ui.details)
        self.assertEqual(self.ui.details.title, "Выбрать")

    def test_refresh_reads_external_changes(self) -> None:
        self.storage.add(Task(title="Извне"))

        self.manager.refresh()

        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(len(self.ui.shown), 1)
        self.assertIsNone(self.ui.details)

    def test_long_title_is_rejected(self) -> None:
        self.ui.inputs = {"title": "x" * 121, "description": "", "author": ""}

        self.manager.create_task()

        self.assertEqual(self.storage.load(), [])
        self.assertEqual(len(self.ui.warnings), 1)

    def test_actions_are_bound(self) -> None:
        self.assertTrue(self.ui.built)
        self.assertEqual(
            set(self.ui.actions),
            {"new", "save", "delete", "toggle", "select", "refresh", "quit"},
        )

    def test_new_action_clears_form_and_selection(self) -> None:
        self.storage.add(Task(title="Старая"))
        self.manager.refresh()
        self.ui.selection = 0
        self.ui.inputs = {"title": "черновик", "description": "", "author": ""}

        self.manager.start_new_task()

        self.assertEqual(self.ui.inputs["title"], "")
        self.assertIsNone(self.ui.selection)
        self.assertIsNone(self.ui.details)
        self.assertTrue(self.ui.focused)

    def test_save_without_selection_creates_task(self) -> None:
        self.ui.selection = None
        self.ui.inputs = {"title": "Через Сохранить", "description": "", "author": ""}

        self.manager.save_task()

        self.assertEqual(len(self.storage.load()), 1)
        self.assertEqual(self.storage.load()[0].title, "Через Сохранить")

    def test_save_with_selection_edits_task(self) -> None:
        self.storage.add(Task(title="Старая"))
        self.manager.refresh()
        self.ui.selection = 0
        self.ui.inputs = {"title": "Новая", "description": "", "author": ""}

        self.manager.save_task()

        tasks = self.storage.load()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Новая")


if __name__ == "__main__":
    unittest.main()
