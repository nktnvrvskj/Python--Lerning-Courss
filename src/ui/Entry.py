"""Однострочное поле ввода приложения."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppEntry(tk.Entry):
    """Наследник tk.Entry со светлым оформлением."""

    def __init__(self, master, **kwargs) -> None:
        options = {
            "bg": theme.CARD,
            "fg": theme.TEXT,
            "insertbackground": theme.TEXT,
            "disabledbackground": theme.SOFT,
            "disabledforeground": theme.MUTED,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": theme.BORDER,
            "highlightcolor": theme.ACCENT,
            "font": theme.FONT,
        }
        options.update(kwargs)

        super().__init__(master, **options)

    def get_value(self) -> str:
        """Вернуть введённый текст без пробелов по краям."""
        return self.get().strip()

    def set_value(self, value: str) -> None:
        """Заменить содержимое поля."""
        self.delete(0, tk.END)
        self.insert(0, "" if value is None else str(value))

    def clear_value(self) -> None:
        """Очистить поле."""
        self.delete(0, tk.END)
