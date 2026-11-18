# Парсер комментариев Hacker News

Учебная работа на requests, BeautifulSoup4, lxml, SQLite и unittest.
Нужен Python 3.12 или новее. Все команды выполняются из корня проекта.

## Установка и запуск в PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Комментарии сохраняются в comments.db рядом с main.py. При повторном запуске
сохранённые ID пропускаются. URL темы можно изменить в main.py.
Слишком длинные сообщения не обрезаются: add выдаёт ValueError.

## Файлы

- src/database.py — класс DatabaseRepository и таблица comments.
- src/parser.py — класс ForumParser, сбор и сохранение комментариев.
- main.py — пример запуска.
- tests/test_database.py — простые проверки всех пяти методов БД.
- tests/test_parser.py — проверки парсера без интернета.
- tests/fixtures/forum.html — сохранённый HTML для тестов.

В существующей папке venv оставлены короткие файлы совместимости, чтобы
сохранить старый запуск venv/main.py в PyCharm. Основной код находится в src.

## База данных

Конструктор принимает путь к SQLite или :memory:. Одна таблица comments:
id INTEGER PRIMARY KEY, name TEXT NOT NULL (до 256 символов),
message TEXT NOT NULL (до 8096 символов).

- get_by_id(comment_id): словарь id/name/message или None.
- get_by_name(username): список записей автора, при отсутствии — [].
- add(comment_id, username, message): True при успехе. Неверный тип — TypeError,
  превышение длины — ValueError, повтор ID — sqlite3.IntegrityError.
- update(comment_id, new_message), delete(comment_id): True, если запись найдена,
  иначе False. update проверяет тип и длину нового сообщения.

## Парсер

parse_page(url) возвращает список словарей id/user/text. Автор ищется через
comhead и первую ссылку a внутри него. Внутренняя HTML-разметка сохраняется.
Записи без автора, сообщения или числового ID пропускаются. Страница без
блока комментариев возвращает []. Поддерживается разметка Hacker News.
Передаются User-Agent и timeout=20; HTTP-ошибки проверяются raise_for_status.
Ошибки requests передаются вызывающему коду.

save_to_db(parsed_data, repository) вызывает add для каждой записи.
При повторных ID вызывается исключение, как при прямом вызове add.

## Тесты

```powershell
python -m unittest discover -s tests -v
```

Тесты БД используют :memory:. В тестах парсера подменяется только requests.get,
который возвращает локальный HTML. Других тестовых библиотек не требуется.
