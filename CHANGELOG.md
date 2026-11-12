# История изменений

## 0.2.0 — 12.11.2026

### Добавлено

- Модель `Task` с полями `id`, `title`, `description`, `status`, `author`,
  `created_at` и методами `to_dict()` / `from_dict()`.
- `StorageManager`: `load`, `save`, `add`, `update`, `delete`, `get`;
  атомарная запись JSON, восстановление после повреждённого файла,
  автоматическая выдача уникальных id.
- `Interface`: `build`, `get_input`, `set_input`, `clear_input`, `show_tasks`,
  `show_message`, `show_warning`, `ask_confirm`, `get_selected_index`.
- Компоненты `AppFrame`, `AppLabel`, `AppEntry`, `AppText`, `AppButton`,
  `AppListbox`, `AppScrollbar` с единой светлой темой.
- Новый интерфейс в две колонки: список задач и карточка подробностей с
  описанием, автором, статусом, датой и ID; выбор задачи заполняет форму.
- Многострочное поле описания (`AppText`) и полоса прокрутки списка.
- `TaskManager`: `create_task`, `edit_task`, `delete_task`, `toggle_status`,
  `save_task`, `start_new_task`, `select_task`, `refresh`, `run`.
- Валидация ввода и обработка ошибок хранилища.
- Тесты: модель, хранилище, бизнес-логика без GUI, дымовой тест окна.
- Документация: README, `documents/ARCHITECTURE.md`,
  `documents/MIGRATION.md`.

### Изменено

- `src/main.py` — теперь только точка входа, а не класс `App`.
- UI полностью собран из компонентов `App*`, «голый» tkinter остался только
  внутри `Interface`.
- Формат `task.json` расширен; старый формат читается автоматически.

### Удалено

- `src/core.py`, `src/view.py`, `src/storege.py` — заменены классами
  `TaskManager`, `Interface`, `StorageManager`.

## 0.1.0

- Подготовка документации и сборка проекта.
- Монолитное приложение `App` на tkinter, хранение в `task.json`.
