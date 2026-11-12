"""UI-компоненты и прослойка Interface."""
from ui.Button import AppButton
from ui.Entry import AppEntry
from ui.Frame import AppFrame
from ui.Label import AppLabel
from ui.Listbox import AppListbox
from ui.Scrollbar import AppScrollbar
from ui.Text import AppText

__all__ = [
    "AppButton",
    "AppEntry",
    "AppFrame",
    "AppLabel",
    "AppListbox",
    "AppScrollbar",
    "AppText",
    "Interface",
]


def __getattr__(name: str):
    """Ленивый импорт Interface, чтобы избежать циклического импорта."""
    if name == "Interface":
        from ui.Interface import Interface

        return Interface
    raise AttributeError(name)
