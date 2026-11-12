"""Подпись приложения."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppLabel(tk.Label):
    """Наследник tk.Label со светлым оформлением."""

    def __init__(self, master, text: str = "", **kwargs) -> None:
        options = {
            "bg": theme.CARD,
            "fg": theme.TEXT,
            "font": theme.FONT,
            "anchor": "w",
            "justify": "left",
        }
        options.update(kwargs)

        super().__init__(master, text=text, **options)

    def set_text(self, text: str) -> None:
        """Обновить текст подписи."""
        self.config(text=text)
