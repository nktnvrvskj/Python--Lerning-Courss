"""Дымовой тест реального окна tkinter (пропускается без дисплея)."""
from __future__ import annotations

import sys
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from storage_manager import StorageManager  # noqa: E402
from task_manager import TaskManager  # noqa: E402
from ui.Interface import Interface  # noqa: E402


def _display_available() -> bool:
    try:
        probe = tk.Tk()
        probe.destroy()
        return True
    except tk.TclError:
        return False


@unittest.skipUnless(_display_available(), "нет графического дисплея")
class GuiSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tasks.json"
        self.interface = Interface()
        self.manager = TaskManager(
            storage=StorageManager(self.path), interface=self.interface
        )

    def tearDown(self) -> None:
        try:
            self.interface.root.destroy()
        except tk.TclError:
            pass
        self.temp_dir.cleanup()

    def test_full_crud_through_widgets(self) -> None:
        root = self.interface.root
        root.update_idletasks()

        self.interface.set_input(
            {"title": "GUI-задача", "description": "описание", "author": "Аня"}
        )
        self.manager.create_task()
        root.update_idletasks()

        self.assertEqual(self.interface.listbox.size(), 1)
        self.assertEqual(len(self.manager.storage.load()), 1)
        # новая задача сразу выбрана, подробности показаны
        self.assertEqual(self.interface.get_selected_index(), 0)
        self.assertEqual(self.interface.detail_title.cget("text"), "GUI-задача")
        self.assertEqual(self.interface.detail_description.cget("text"), "описание")

        self.interface.select_index(0)
        self.manager.select_task()
        self.assertEqual(self.interface.get_input()["title"], "GUI-задача")

        self.interface.set_input(
            {"title": "GUI-задача (изменена)", "description": "новое", "author": "Иван"}
        )
        self.manager.edit_task()
        root.update_idletasks()

        self.assertEqual(self.manager.storage.load()[0].title, "GUI-задача (изменена)")
        self.assertEqual(self.interface.listbox.size(), 1)

        self.interface.select_index(0)
        self.manager.toggle_status()
        root.update_idletasks()
        self.assertTrue(self.manager.storage.load()[0].status)

        self.interface.select_index(0)
        with mock.patch.object(self.interface, "ask_confirm", return_value=True):
            self.manager.delete_task()
        root.update_idletasks()

        self.assertEqual(self.interface.listbox.size(), 0)
        self.assertEqual(self.manager.storage.load(), [])

    def test_buttons_are_wired(self) -> None:
        root = self.interface.root
        root.update_idletasks()

        self.assertIsNotNone(self.interface.title_entry)
        self.assertIsNotNone(self.interface.description_entry)
        self.assertIsNotNone(self.interface.author_entry)
        self.assertIsNotNone(self.interface.listbox)
        self.assertIsNotNone(self.interface.details_placeholder)
        self.assertTrue(self.interface.details_placeholder.winfo_ismapped())
        self.assertFalse(self.interface.details_content.winfo_ismapped())
        self.assertEqual(root.title(), "Менеджер задач v0.2.0")
        self.assertEqual(
            set(self.interface.actions),
            {"new", "save", "delete", "toggle", "select", "refresh", "quit"},
        )


if __name__ == "__main__":
    unittest.main()
