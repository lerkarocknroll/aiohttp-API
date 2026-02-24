# aiohttp API для объявлений

REST API на aiohttp для работы с объявлениями: создание, чтение, обновление, удаление.  
Валидация - Pydantic, база данных - PostgreSQL (асинхронный драйвер asyncpg), окружение - Docker.

---

## Технологии
- Python 3.11
- aiohttp 3.9.5
- SQLAlchemy 1.4.53 (асинхронный режим)
- asyncpg 0.29.0
- PostgreSQL
- Pydantic 2.10.6
- Docker, Docker Compose

---

## Запуск

### Через Docker
```bash
docker-compose up --build
```
После запуска сервер доступен на http://localhost:8000.

**Остановка:**
```bash
docker-compose down
```
Удаление томов БД:
```bash
docker-compose down -v
```

### Локально без Docker
1. Установите PostgreSQL, создайте базу и пользователя:
   ```sql
   CREATE DATABASE advertisements_flask_db;
   CREATE USER user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE advertisements_flask_db TO user;
   ```
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate          # Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Убедитесь, что переменная окружения `PG_DSN` указывает на вашу БД (по умолчанию используется `postgresql+asyncpg://user:password@localhost:5432/advertisements_flask_db`).
5. Запустите сервер:
   ```bash
   python server.py
   ```
Сервер будет доступен на http://localhost:8000.

---

## API Endpoints

| Метод | URL | Назначение | Тело запроса (JSON) |
|-------|-----|------------|----------------------|
| POST | `/advertisements` | Создать объявление | `{"title": "...", "description": "...", "owner": "..."}` |
| GET | `/advertisements/{id}/` | Получить объявление | – |
| PATCH | `/advertisements/{id}/` | Обновить объявление | `{"title": "...", "description": "...", "owner": "..."}` (поля необязательны) |
| DELETE | `/advertisements/{id}/` | Удалить объявление | – |

---

## Примеры запросов (curl)

### Создание
```bash
curl -X POST http://localhost:8000/advertisements \
  -H "Content-Type: application/json" \
  -d '{"title": "Продам велосипед", "description": "Горный, 26 дюймов", "owner": "Иван"}'
```
**Ответ:** 201 Created
```json
{
  "id": 1,
  "title": "Продам велосипед",
  "description": "Горный, 26 дюймов",
  "owner": "Иван"
}
```

### Получение
```bash
curl http://localhost:8000/advertisements/1/
```
**Ответ:** 200 OK
```json
{
  "id": 1,
  "title": "Продам велосипед",
  "description": "Горный, 26 дюймов",
  "created_at": "2026-02-12T10:15:30",
  "owner": "Иван"
}
```
Если запись не найдена — 404 Not Found.

### Обновление
```bash
curl -X PATCH http://localhost:8000/advertisements/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Продам горный велосипед"}'
```
**Ответ:** 200 OK
```json
{
  "id": 1,
  "title": "Продам горный велосипед",
  "description": "Горный, 26 дюймов",
  "owner": "Иван"
}
```

### Удаление
```bash
curl -X DELETE http://localhost:8000/advertisements/1/
```
**Ответ:** 200 OK
```json
{
  "status": "success"
}
```
При повторном запросе — 404 Not Found.

---

## Тестирование
Скрипт `requests_api.py` выполняет последовательность запросов: создание → получение → обновление → удаление → проверка отсутствия.

Запуск:
```bash
python requests_api.py
```
Или внутри контейнера:
```bash
docker exec -it flask-main-app-1 python requests_api.py
```

---

## Структура проекта
```
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── server.py          # точка входа, инициализация aiohttp‑приложения
├── models.py          # модели SQLAlchemy и Pydantic
├── views.py           # асинхронные обработчики запросов
├── routes.py          # маршруты (RouteTableDef)
├── requests_api.py    # тестовый клиент
└── README.md
```

---

**Автор:** Валерия
