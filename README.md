# Food Price Analytics

Веб-сервис на Django для мониторинга и анализа динамики цен на продукты питания. Позволяет отслеживать стоимость товаров в различных магазинах, анализировать изменения цен во времени и управлять списками покупок.

## Функциональность

*   **Каталог товаров:** Просмотр, добавление и редактирование товаров с изображениями.
*   **Категории:** Структурированный список товаров (Молочные продукты, Бакалея и т.д.).
*   **Магазины:** Справочник магазинов с ссылками.
*   **Мониторинг цен:** Учет истории цен (PriceRecord) для каждого товара.
*   **Аналитика:** Дэшборд для визуализации данных и динамики цен (использует Pandas и Chart.js).
*   **Списки покупок:** Персональные списки для зарегистрированных пользователей.
*   **Импорт/Экспорт:** Инструменты для загрузки и выгрузки данных.

## Технологический стек

*   **Python** 3.11+
*   **Django** 5.x
*   **uv** — современный менеджер пакетов (вместо pip/poetry)
*   **Pandas** — обработка и анализ данных
*   **Tailwind CSS** — стилизация интерфейса
*   **SQLite** — база данных

## Установка и запуск

Проект полностью управляется через **uv**.

### 1. Установка uv

Если uv еще не установлен:
```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Клонирование и установка зависимостей

```bash
git clone <url-to-repo>
cd food_price_analysis

# Создание виртуального окружения и синхронизация зависимостей из pyproject.toml
uv sync
```

### 3. Настройка базы данных

Примените миграции:
```bash
uv run python manage.py migrate
```

### 4. Наполнение тестовыми данными

В проекте есть команда для генерации каталога, магазинов и истории цен:
```bash
uv run python manage.py seed_db
```
*Используйте флаг `--clean`, если хотите предварительно очистить базу данных.*

### 5. Запуск сервера

```bash
uv run python manage.py runserver
```
Сайт будет доступен по адресу: http://127.0.0.1:8000/

### 6. Работа с Tailwind CSS (для разработки фронтенда)

Если вы планируете менять стили, вам понадобится Node.js.
Установка зависимостей темы:
```bash
uv run python manage.py tailwind install
```
Запуск вотчера для компиляции CSS в реальном времени:
```bash
uv run python manage.py tailwind start
```

## Структура проекта

*   `analytics/` — Основное приложение:
    *   `models.py`: Модели Product, Store, PriceRecord, ShoppingList.
    *   `views.py`: Представления для дэшборда, списков и форм.
    *   `management/commands/seed_db.py`: Скрипт генерации данных.
*   `config/` — Конфигурация Django проекта.
*   `theme/` — Приложение стилей (Django Tailwind).
*   `templates/` — HTML шаблоны.
*   `pyproject.toml` — Управление зависимостями проекта.

## Скриншоты

Главная
<img width="1852" height="934" alt="image" src="https://github.com/user-attachments/assets/9387380f-cde3-47de-8955-f3d9d8d92577" />
Дашборд
<img width="1608" height="922" alt="image" src="https://github.com/user-attachments/assets/f99eef04-3db1-44c2-804f-9b3408c762b9" />
<img width="1594" height="632" alt="image" src="https://github.com/user-attachments/assets/ada379ed-a2f9-4d7f-a54f-26e55f7b025d" />
Товары для администратора
<img width="1471" height="852" alt="image" src="https://github.com/user-attachments/assets/3f6fbb92-64c6-4852-8800-7a21cc26fc88" />

