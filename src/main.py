"""Точка входа приложения «Менеджер задач v0.2.0».

Запуск:
    python src/main.py

main.py только собирает TaskManager и запускает приложение — вся логика
находится в классах Task, StorageManager, Interface и TaskManager.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Разрешаем запуск как `python src/main.py` из любой папки.
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from task_manager import TaskManager  # noqa: E402


def main() -> None:
    """Создать TaskManager и запустить приложение."""
    app = TaskManager()
    app.run()


if __name__ == "__main__":
    main()
