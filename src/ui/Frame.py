"""Контейнер (фрейм) приложения."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppFrame(tk.Frame):
    """Наследник tk.Frame со светлым оформлением."""

    def __init__(self, master, **kwargs) -> None:
        options = {
            "bg": theme.CARD,
            "borderwidth": 0,
            "highlightthickness": 0,
            "relief": "flat",
        }
        options.update(kwargs)

        super().__init__(master, **options)
