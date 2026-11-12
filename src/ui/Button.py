"""Кнопка приложения с единым стилем."""
from __future__ import annotations

import tkinter as tk

from ui import theme


class AppButton(tk.Button):
    """Наследник tk.Button с простыми вариантами оформления."""

    _VARIANTS = {
        "primary": (theme.ACCENT, theme.ACCENT_ACTIVE, "#ffffff"),
        "secondary": (theme.SOFT, theme.SOFT_ACTIVE, theme.TEXT),
        "danger": ("#fef2f2", "#fee2e2", theme.DANGER),
    }

    def __init__(self, master, text: str, command, variant: str = "primary", **kwargs) -> None:
        background, active_background, foreground = self._VARIANTS.get(
            variant, self._VARIANTS["primary"]
        )

        options = {
            "bg": background,
            "fg": foreground,
            "activebackground": active_background,
            "activeforeground": foreground,
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 0,
            "cursor": "hand2",
            "font": theme.FONT_BOLD,
            "padx": 12,
            "pady": 6,
        }
        options.update(kwargs)

        super().__init__(master, text=text, command=command, **options)
