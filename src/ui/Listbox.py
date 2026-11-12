"""Список задач приложения."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppListbox(tk.Listbox):
    """Наследник tk.Listbox со светлым оформлением."""

    def __init__(self, master, **kwargs) -> None:
        options = {
            "bg": theme.CARD,
            "fg": theme.TEXT,
            "selectbackground": theme.SELECT_BG,
            "selectforeground": theme.SELECT_FG,
            "activestyle": "none",
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 0,
            "font": theme.FONT,
            "height": 12,
            "exportselection": False,
        }
        options.update(kwargs)

        super().__init__(master, **options)

    def set_items(self, items: list[str]) -> None:
        """Полностью заменить содержимое списка."""
        self.delete(0, tk.END)
        for item in items:
            self.insert(tk.END, item)

    def selected_index(self) -> int | None:
        """Индекс выбранной строки или None."""
        selection = self.curselection()
        return int(selection[0]) if selection else None

    def select_index(self, index: int) -> None:
        """Выделить строку по индексу и прокрутить к ней список."""
        self.selection_clear(0, tk.END)
        self.selection_set(index)
        self.activate(index)
        self.see(index)
