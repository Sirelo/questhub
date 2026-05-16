# QuestHub

QuestHub — веб-приложение на Flask, где прогулки, учебные спринты, творческие идеи и полезные привычки оформляются как короткие экспедиции. Пользователь может создать свой маршрут, присоединиться к чужому, отмечать прогресс и следить за рейтингом.

## Возможности

- регистрация и авторизация;
- редактирование профиля;
- создание и редактирование экспедиций;
- поиск и фильтрация по ленте;
- участие в чужих экспедициях;
- ежедневные `check-in` отметки;
- комментарии;
- рейтинг пользователей;
- бейджи;
- REST API со статистикой.

## Стек

- Python 3.11+
- Flask
- Flask-Login
- Flask-WTF
- SQLite / `sqlite3`
- Bootstrap 5

## Структура

```text
app/
  blueprints/      # маршруты
  forms/           # формы
  models/          # dataclass-модели
  repository.py    # SQL-запросы и слой доступа к данным
  services/        # бизнес-логика
  static/          # стили и загрузки
  templates/       # шаблоны
tests/             # тесты
run.py             # точка входа
```

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Приложение само создаст таблицы и заполнит пустую базу демо-данными.

## Демо-аккаунты

Все демо-пользователи создаются с паролем `password123`:

- `alice@example.com`
- `misha@example.com`
- `sonya@example.com`
- `timur@example.com`
- `lena@example.com`
- `artem@example.com`

## API

- `GET /api/expeditions`
- `GET /api/expeditions/<id>`
- `GET /api/users/<id>/stats`
- `GET /api/leaderboard`
