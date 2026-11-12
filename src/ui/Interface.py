"""Interface — прослойка между логикой и tkinter.

Класс ничего не знает про задачи и StorageManager. Он умеет только:
* строить окно из компонентов App*;
* отдавать введённые пользователем данные;
* показывать список, подробности выбранной задачи и диалоги.

TaskManager общается с интерфейсом только через эти методы.
"""
from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

from ui import theme
from ui.Button import AppButton
from ui.Entry import AppEntry
from ui.Frame import AppFrame
from ui.Label import AppLabel
from ui.Listbox import AppListbox
from ui.Scrollbar import AppScrollbar
from ui.Text import AppText


class Interface:
    """Фасад над tkinter: единый API для TaskManager."""

    def __init__(
        self,
        title: str = "Менеджер задач v0.2.0",
        width: int = 900,
        height: int = 740,
    ) -> None:
        """Создать корневое окно и настроить его."""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(820, 660)
        self.root.configure(bg=theme.BG)

        self.actions: dict[str, Callable[[], None]] = {}
        self._tasks: list = []
        self._current_task = None
        self._built = False

        # Ссылки на виджеты создаются в build().
        self.title_entry: AppEntry | None = None
        self.description_entry: AppText | None = None
        self.author_entry: AppEntry | None = None
        self.listbox: AppListbox | None = None
        self.count_label: AppLabel | None = None
        self.status_label: AppLabel | None = None

        self.details_content: AppFrame | None = None
        self.details_placeholder: AppLabel | None = None
        self.detail_title: AppLabel | None = None
        self.detail_status: AppLabel | None = None
        self.detail_description: AppLabel | None = None
        self.detail_meta: AppLabel | None = None

        self._set_icon()

    # ---------- жизненный цикл ----------
    def run(self) -> None:
        """Запустить главный цикл tkinter."""
        self.root.mainloop()

    def quit(self) -> None:
        """Закрыть окно."""
        self.root.destroy()

    def clear(self) -> None:
        """Удалить все дочерние виджеты (используется при пересборке)."""
        for child in self.root.winfo_children():
            child.destroy()
        self.title_entry = None
        self.description_entry = None
        self.author_entry = None
        self.listbox = None
        self.count_label = None
        self.status_label = None
        self.details_content = None
        self.details_placeholder = None
        self.detail_title = None
        self.detail_status = None
        self.detail_description = None
        self.detail_meta = None
        self._current_task = None
        self._built = False

    # ---------- построение ----------
    def set_actions(self, actions: dict) -> None:
        """Привязать колбэки TaskManager к кнопкам интерфейса."""
        self.actions = dict(actions)

    def build(self) -> None:
        """Собрать окно: шапка, список, подробности, форма, кнопки."""
        if self._built:
            return

        self._build_header()
        self._build_status_bar()
        self._build_action_bar()
        self._build_form()
        self._build_main_area()

        self._bind_keys()
        self.show_task_details(None)
        if self.title_entry:
            self.title_entry.focus_set()
        self._built = True

    def _build_header(self) -> None:
        """Шапка: название приложения."""
        header = AppFrame(
            self.root,
            bg=theme.CARD,
            highlightbackground=theme.BORDER,
            highlightthickness=1,
        )
        header.pack(side="top", fill="x")

        inner = AppFrame(header, bg=theme.CARD)
        inner.pack(fill="x", padx=20, pady=12)

        AppLabel(
            inner,
            "Менеджер задач",
            bg=theme.CARD,
            font=theme.FONT_HEADING,
        ).pack(side="left")
        AppLabel(
            inner,
            "v0.2.0",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        ).pack(side="left", padx=(8, 0), pady=(6, 0))

        self.count_label = AppLabel(
            inner,
            "0 задач",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        )
        self.count_label.pack(side="right")

    def _build_status_bar(self) -> None:
        """Статус-строка в самом низу окна."""
        self.status_label = AppLabel(
            self.root,
            "Готово к работе",
            bg=theme.BG,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
            padx=16,
            pady=6,
        )
        self.status_label.pack(side="bottom", fill="x")

    def _build_action_bar(self) -> None:
        """Нижняя панель действий."""
        bar = AppFrame(self.root, bg=theme.BG)
        bar.pack(side="bottom", fill="x", padx=16, pady=(0, 8))

        AppButton(bar, "＋ Новая", lambda: self._invoke("new"), "secondary").pack(
            side="left", padx=(0, 6)
        )
        AppButton(bar, "Сохранить", lambda: self._invoke("save"), "primary").pack(
            side="left", padx=(0, 6)
        )
        AppButton(bar, "Готово", lambda: self._invoke("toggle"), "secondary").pack(
            side="left", padx=(0, 6)
        )
        AppButton(bar, "Удалить", lambda: self._invoke("delete"), "danger").pack(
            side="left"
        )
        AppButton(bar, "Выход", self.quit, "secondary").pack(side="right")

    def _build_form(self) -> None:
        """Форма создания и редактирования задачи."""
        card = AppFrame(
            self.root,
            bg=theme.CARD,
            highlightbackground=theme.BORDER,
            highlightthickness=1,
        )
        card.pack(side="bottom", fill="x", padx=16, pady=(0, 8))
        card.columnconfigure(1, weight=3)
        card.columnconfigure(3, weight=1)

        AppLabel(
            card,
            "Название *",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        ).grid(row=0, column=0, sticky="w", padx=(14, 8), pady=(11, 6))

        self.title_entry = AppEntry(card)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=(11, 6))

        AppLabel(
            card,
            "Автор",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        ).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=(11, 6))

        self.author_entry = AppEntry(card, width=18)
        self.author_entry.grid(row=0, column=3, sticky="ew", padx=(0, 14), pady=(11, 6))

        AppLabel(
            card,
            "Описание",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        ).grid(row=1, column=0, sticky="nw", padx=(14, 8), pady=(0, 11))

        self.description_entry = AppText(card, height=3)
        self.description_entry.grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=(0, 14), pady=(0, 11)
        )

    def _build_main_area(self) -> None:
        """Две колонки: список задач и подробности выбранной задачи."""
        main = AppFrame(self.root, bg=theme.BG)
        main.pack(side="top", fill="both", expand=True, padx=16, pady=12)
        main.columnconfigure(0, weight=1, minsize=420)
        main.columnconfigure(1, weight=0, minsize=320)
        main.rowconfigure(0, weight=1)

        # Список задач
        list_card = AppFrame(
            main,
            bg=theme.CARD,
            highlightbackground=theme.BORDER,
            highlightthickness=1,
        )
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        list_header = AppFrame(list_card, bg=theme.CARD)
        list_header.pack(fill="x", padx=14, pady=(11, 7))
        AppLabel(
            list_header,
            "Задачи",
            bg=theme.CARD,
            font=theme.FONT_CARD,
        ).pack(side="left")

        list_body = AppFrame(list_card, bg=theme.CARD)
        list_body.pack(fill="both", expand=True, padx=(14, 8), pady=(0, 14))

        scroll = AppScrollbar(list_body)
        scroll.pack(side="right", fill="y")
        self.listbox = AppListbox(list_body, yscrollcommand=scroll.set, height=12)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Delete>", lambda _event: self._invoke("delete"))

        # Подробности
        self.details_card = AppFrame(
            main,
            bg=theme.CARD,
            highlightbackground=theme.BORDER,
            highlightthickness=1,
        )
        self.details_card.grid(row=0, column=1, sticky="nsew")
        self.details_card.bind("<Configure>", self._resize_details)

        details_header = AppFrame(self.details_card, bg=theme.CARD)
        details_header.pack(fill="x", padx=14, pady=(11, 7))
        AppLabel(
            details_header,
            "Подробности",
            bg=theme.CARD,
            font=theme.FONT_CARD,
        ).pack(side="left")

        body = AppFrame(self.details_card, bg=theme.CARD)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        self.details_placeholder = AppLabel(
            body,
            "Выберите задачу слева,\nчтобы увидеть описание.",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT,
            anchor="center",
            justify="center",
        )

        self.details_content = AppFrame(body, bg=theme.CARD)

        self.detail_title = AppLabel(
            self.details_content,
            "",
            bg=theme.CARD,
            font=theme.FONT_DETAIL_TITLE,
            wraplength=280,
        )
        self.detail_title.pack(fill="x", anchor="w")

        self.detail_status = AppLabel(
            self.details_content,
            "",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        )
        self.detail_status.pack(fill="x", anchor="w", pady=(4, 10))

        separator = AppFrame(self.details_content, bg=theme.BORDER, height=1)
        separator.pack(fill="x", pady=(0, 10))

        AppLabel(
            self.details_content,
            "ОПИСАНИЕ",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
        ).pack(fill="x", anchor="w")

        self.detail_description = AppLabel(
            self.details_content,
            "",
            bg=theme.CARD,
            font=theme.FONT,
            wraplength=280,
            justify="left",
            anchor="w",
        )
        self.detail_description.pack(fill="x", anchor="w", pady=(3, 14))

        self.detail_meta = AppLabel(
            self.details_content,
            "",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=theme.FONT_SMALL,
            justify="left",
            anchor="w",
        )
        self.detail_meta.pack(fill="x", anchor="w")

    def _resize_details(self, event) -> None:
        """Подогнать перенос строк под ширину панели подробностей."""
        wrap = max(180, event.width - 40)
        if self.detail_title:
            self.detail_title.config(wraplength=wrap)
        if self.detail_description:
            self.detail_description.config(wraplength=wrap)

    def _bind_keys(self) -> None:
        """Горячие клавиши окна."""
        self.root.bind("<Control-n>", lambda _event: self._invoke("new"))
        self.root.bind("<Control-s>", lambda _event: self._invoke("save"))
        self.root.bind("<Control-Return>", lambda _event: self._invoke("save"))
        self.root.bind("<F5>", lambda _event: self._invoke("refresh"))
        self.root.bind("<Escape>", lambda _event: self.quit())
        self.root.bind("<Return>", lambda _event: self._invoke("save"))

    def _set_icon(self) -> None:
        """Поставить иконку приложения, если платформа её поддерживает."""
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icon.ico"
        if not icon_path.exists():
            return
        try:
            self.root.iconbitmap(default=str(icon_path))
        except tk.TclError:
            # На Linux iconbitmap для .ico может быть недоступен — это не критично.
            pass

    # ---------- ввод ----------
    def get_input(self) -> dict:
        """Вернуть {title, description, author} из полей ввода."""
        return {
            "title": self.title_entry.get_value() if self.title_entry else "",
            "description": (
                self.description_entry.get_value() if self.description_entry else ""
            ),
            "author": self.author_entry.get_value() if self.author_entry else "",
        }

    def set_input(self, data) -> None:
        """Заполнить поля данными Task или словаря."""
        payload = data.to_dict() if hasattr(data, "to_dict") else dict(data or {})
        if self.title_entry:
            self.title_entry.set_value(payload.get("title", ""))
        if self.description_entry:
            self.description_entry.set_value(payload.get("description", ""))
        if self.author_entry:
            self.author_entry.set_value(payload.get("author", ""))

    def clear_input(self) -> None:
        """Очистить поля ввода."""
        for entry in (self.title_entry, self.description_entry, self.author_entry):
            if entry:
                entry.clear_value()

    def focus_title(self) -> None:
        """Поставить курсор в поле «Название»."""
        if self.title_entry:
            self.title_entry.focus_set()

    # ---------- отображение ----------
    def show_tasks(self, tasks: list) -> None:
        """Заполнить список задач (list[Task] или list[dict])."""
        self._tasks = list(tasks)
        lines: list[str] = []

        for task in self._tasks:
            data = task.to_dict() if hasattr(task, "to_dict") else dict(task)
            title = str(data.get("title") or data.get("name") or "")
            mark = "✓" if data.get("status") else "•"
            line = f" {mark}  {title}"
            if len(line) > 60:
                line = line[:59] + "…"
            lines.append(line)

        if self.listbox:
            self.listbox.set_items(lines)
        if self.count_label:
            self.count_label.set_text(self._tasks_label(len(lines)))

    def show_task_details(self, task) -> None:
        """Показать карточку выбранной задачи или подсказку, если её нет."""
        if not self.details_content or not self.details_placeholder:
            return

        self._current_task = task

        if task is None:
            self.details_content.pack_forget()
            self.details_placeholder.pack(fill="both", expand=True)
            return

        payload = task.to_dict() if hasattr(task, "to_dict") else dict(task)
        title = str(payload.get("title") or payload.get("name") or "Без названия")
        description = str(payload.get("description") or "").strip()
        author = str(payload.get("author") or "—")
        created_at = self._format_date(payload.get("created_at"))
        task_id = payload.get("id")

        if self.detail_title:
            self.detail_title.set_text(title)
        if self.detail_status:
            if payload.get("status"):
                self.detail_status.config(text="●  Выполнена", fg=theme.SUCCESS)
            else:
                self.detail_status.config(text="○  Активна", fg=theme.MUTED)
        if self.detail_description:
            self.detail_description.set_text(description or "Описание не добавлено.")
        if self.detail_meta:
            self.detail_meta.set_text(
                f"Автор: {author}\nСоздана: {created_at}\nID: {task_id}"
            )

        self.details_placeholder.pack_forget()
        self.details_content.pack(fill="both", expand=True)

    def show_message(self, title: str, text: str) -> None:
        """Показать информационное сообщение в статус-строке."""
        message = f"{title}: {text}" if title else text
        if self.status_label:
            self.status_label.config(fg=theme.MUTED, text=message)

    def show_warning(self, title: str, text: str) -> None:
        """Показать предупреждение в отдельном диалоге."""
        if self.status_label:
            self.status_label.config(fg=theme.DANGER, text=f"{title}: {text}")
        messagebox.showwarning(title, text, parent=self.root)

    def ask_confirm(self, title: str, text: str) -> bool:
        """Спросить подтверждение. True — да, False — нет."""
        return bool(messagebox.askyesno(title, text, parent=self.root))

    # ---------- выделение ----------
    def get_selected_index(self) -> int | None:
        """Индекс выбранной строки в списке или None."""
        return self.listbox.selected_index() if self.listbox else None

    def select_index(self, index: int) -> None:
        """Выделить строку списка по индексу."""
        if self.listbox and 0 <= index < self.listbox.size():
            self.listbox.select_index(index)

    def clear_selection(self) -> None:
        """Снять выделение со списка задач."""
        if self.listbox:
            self.listbox.selection_clear(0, tk.END)

    # ---------- события ----------
    def _on_select(self, _event=None) -> None:
        """Сообщить TaskManager, что пользователь выбрал задачу."""
        if self.get_selected_index() is not None:
            self._invoke("select")

    def _invoke(self, name: str) -> None:
        """Вызвать действие TaskManager по имени."""
        action = self.actions.get(name)
        if action is None:
            return
        try:
            action()
        except Exception as exc:  # защита UI от необработанных исключений
            self.show_warning("Ошибка", str(exc))

    # ---------- вспомогательное ----------
    @staticmethod
    def _format_date(value) -> str:
        """ISO-дату превратить в читаемый вид."""
        if not value:
            return "—"
        try:
            return datetime.fromisoformat(str(value)).strftime("%d.%m.%Y, %H:%M")
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def _tasks_label(count: int) -> str:
        """Склонение слова «задача» для счётчика."""
        if count % 10 == 1 and count % 100 != 11:
            word = "задача"
        elif 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
            word = "задачи"
        else:
            word = "задач"
        return f"{count} {word}"
