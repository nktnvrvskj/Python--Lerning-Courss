"""Многострочное поле для описания задачи."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppText(tk.Text):
    """Наследник tk.Text в стиле остальных полей приложения."""

    def __init__(self, master, **kwargs) -> None:
        options = {
            "bg": theme.CARD,
            "fg": theme.TEXT,
            "insertbackground": theme.TEXT,
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 1,
            "highlightbackground": theme.BORDER,
            "highlightcolor": theme.ACCENT,
            "font": theme.FONT,
            "height": 3,
            "wrap": "word",
            "padx": 6,
            "pady": 4,
        }
        options.update(kwargs)

        super().__init__(master, **options)

    def get_value(self) -> str:
        """Вернуть текст без завершающего перевода строки."""
        return self.get("1.0", "end-1c").strip()

    def set_value(self, value: str) -> None:
        """Заменить содержимое."""
        self.delete("1.0", tk.END)
        self.insert("1.0", "" if value is None else str(value))

    def clear_value(self) -> None:
        """Очистить поле."""
        self.delete("1.0", tk.END)
