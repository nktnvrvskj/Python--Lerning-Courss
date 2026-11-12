"""Полоса прокрутки приложения."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppScrollbar(tk.Scrollbar):
    """Наследник tk.Scrollbar с тонким светлым оформлением."""

    def __init__(self, master, **kwargs) -> None:
        options = {
            "bg": theme.BORDER,
            "troughcolor": theme.CARD,
            "activebackground": theme.MUTED,
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 0,
            "width": 10,
        }
        options.update(kwargs)

        super().__init__(master, **options)
