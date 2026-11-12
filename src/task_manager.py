"""TaskManager — фасад приложения.

Связывает модель (Task), хранилище (StorageManager) и интерфейс (Interface).
Здесь находится вся бизнес-логика CRUD; tkinter напрямую не используется.
"""
from __future__ import annotations

from config import NAME_FILES_SAVES
from storage_manager import StorageError, StorageManager
from task import Task
from ui.Interface import Interface

TITLE_MAX = 120
DESCRIPTION_MAX = 500
AUTHOR_MAX = 60


class TaskManager:
    """Оркестратор приложения. Единственная точка входа для UI."""

    def __init__(self, storage: StorageManager | None = None, interface=None) -> None:
        """Создать хранилище и интерфейс, привязать колбэки."""
        self.storage = storage if storage is not None else StorageManager(NAME_FILES_SAVES)
        self.interface = interface if interface is not None else Interface()
        self.tasks: list[Task] = []

        self.interface.set_actions(
            {
                "new": self.start_new_task,
                "save": self.save_task,
                "delete": self.delete_task,
                "toggle": self.toggle_status,
                "select": self.select_task,
                "refresh": self.refresh,
                "quit": self.interface.quit,
            }
        )
        self.interface.build()
        self.refresh()

    # ---------- CRUD ----------
    def start_new_task(self) -> None:
        """Подготовить форму для новой задачи: очистить поля и выделение."""
        self.interface.clear_selection()
        self.interface.clear_input()
        self.interface.show_task_details(None)
        if hasattr(self.interface, "focus_title"):
            self.interface.focus_title()
        self.interface.show_message(
            "Новая задача", "Заполните поля и нажмите «Сохранить»."
        )

    def save_task(self) -> None:
        """Сохранить форму: создать новую задачу или обновить выбранную."""
        if self.interface.get_selected_index() is None:
            self.create_task()
        else:
            self.edit_task()

    def create_task(self) -> None:
        """Прочитать ввод → создать Task → сохранить → обновить список."""
        data = self._read_form()
        if data is None:
            return

        try:
            task = Task(**data)
            self.storage.add(task)
        except ValueError as exc:
            self.interface.show_warning("Проверка ввода", str(exc))
            return
        except StorageError as exc:
            self.interface.show_warning("Ошибка сохранения", str(exc))
            return

        self.refresh(select_id=task.id)
        saved = self.storage.get(task.id) or task
        self.interface.set_input(saved)
        self.interface.show_message(
            "Задача создана", f"«{task.title}» сохранена (id={task.id})."
        )

    def edit_task(self) -> None:
        """Взять выбранную задачу → изменить → сохранить → обновить."""
        task = self._selected_task()
        if task is None:
            self.interface.show_warning(
                "Задача не выбрана",
                "Сначала выберите задачу в списке, затем измените поля и нажмите «Сохранить».",
            )
            return

        data = self._read_form()
        if data is None:
            return

        updated = Task(
            id=task.id,
            title=data["title"],
            description=data["description"],
            status=task.status,
            author=data["author"],
            created_at=task.created_at,
        )

        try:
            self.storage.update(task.id, updated)
        except StorageError as exc:
            self.interface.show_warning("Ошибка сохранения", str(exc))
            return

        self.refresh(select_id=task.id)
        self.interface.set_input(updated)
        self.interface.show_message("Задача обновлена", f"«{updated.title}» сохранена.")

    def delete_task(self) -> None:
        """Удалить выбранную задачу (с подтверждением)."""
        task = self._selected_task()
        if task is None:
            self.interface.show_warning(
                "Задача не выбрана", "Сначала выберите задачу в списке."
            )
            return

        if not self.interface.ask_confirm(
            "Удаление задачи", f"Удалить задачу «{task.title}»? Это действие необратимо."
        ):
            return

        try:
            deleted = self.storage.delete(task.id)
        except StorageError as exc:
            self.interface.show_warning("Ошибка сохранения", str(exc))
            return

        if not deleted:
            self.interface.show_warning(
                "Задача не найдена", "Возможно, она уже была удалена. Список обновлён."
            )

        self.interface.clear_input()
        self.refresh()
        if deleted:
            self.interface.show_message("Задача удалена", f"«{task.title}» удалена.")

    def toggle_status(self) -> None:
        """Переключить статус выбранной задачи."""
        task = self._selected_task()
        if task is None:
            self.interface.show_warning(
                "Задача не выбрана", "Сначала выберите задачу в списке."
            )
            return

        task.toggle()
        try:
            self.storage.update(task.id, task)
        except StorageError as exc:
            task.toggle()  # откатываем изменение, если запись не удалась
            self.interface.show_warning("Ошибка сохранения", str(exc))
            return

        self.refresh(select_id=task.id)
        state = "выполнена" if task.status else "снова активна"
        self.interface.show_message("Статус изменён", f"Задача «{task.title}» {state}.")

    def toggle_done(self) -> None:
        """Синоним toggle_status (название из методички)."""
        self.toggle_status()

    # ---------- служебное ----------
    def select_task(self) -> None:
        """Показать выбранную задачу в полях ввода."""
        task = self._selected_task()
        if task is None:
            return

        self.interface.set_input(task)
        self.interface.show_task_details(task)
        self.interface.show_message(
            "Выбрана задача", f"id={task.id} · «{task.title}»."
        )

    def refresh(self, select_id: int | None = None) -> None:
        """Перечитать задачи из StorageManager и отрисовать."""
        try:
            self.tasks = self.storage.load()
        except StorageError as exc:
            self.interface.show_warning("Ошибка загрузки", str(exc))
            return

        self.interface.show_tasks(self.tasks)

        selected = None
        if select_id is not None:
            for index, task in enumerate(self.tasks):
                if task.id == select_id:
                    self.interface.select_index(index)
                    selected = task
                    break

        self.interface.show_task_details(selected)
        self.interface.show_message("Список обновлён", f"Всего задач: {len(self.tasks)}.")

    def run(self) -> None:
        """Передать управление Interface."""
        self.interface.run()

    # ---------- внутренние помощники ----------
    def _selected_task(self) -> Task | None:
        """Задача, выбранная в списке, либо None."""
        index = self.interface.get_selected_index()
        if index is None or not 0 <= index < len(self.tasks):
            return None
        return self.tasks[index]

    def _read_form(self) -> dict | None:
        """Прочитать и провалидировать поля формы."""
        raw = self.interface.get_input()
        title = str(raw.get("title") or "").strip()
        description = str(raw.get("description") or "").strip()
        author = str(raw.get("author") or "").strip()

        if not title:
            self.interface.show_warning(
                "Проверка ввода", "Поле «Название» обязательно для заполнения."
            )
            return None
        if len(title) > TITLE_MAX:
            self.interface.show_warning(
                "Проверка ввода", f"Название длиннее {TITLE_MAX} символов."
            )
            return None
        if len(description) > DESCRIPTION_MAX:
            self.interface.show_warning(
                "Проверка ввода", f"Описание длиннее {DESCRIPTION_MAX} символов."
            )
            return None
        if len(author) > AUTHOR_MAX:
            self.interface.show_warning(
                "Проверка ввода", f"Имя автора длиннее {AUTHOR_MAX} символов."
            )
            return None

        return {
            "title": title,
            "description": description,
            "author": author or "—",
        }
