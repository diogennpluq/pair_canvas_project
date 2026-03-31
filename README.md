# 🎨 Pair Canvas - Совместное рисование в реальном времени

**Pair Canvas** — это веб-приложение для совместного рисования на одном холсте в реальном времени. Работайте над рисунками вместе с другом, общайтесь в чате и создавайте удивительные арты вместе!

![Django](https://img.shields.io/badge/Django-5.0+-0C4B33?style=flat&logo=django)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![WebSocket](https://img.shields.io/badge/WebSocket-Channels-090909?style=flat&logo=websocket)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat)

## ✨ Возможности

### 🎯 Режимы рисования
- **🎨 Свободное рисование** — оба участника рисуют одновременно без ограничений
- **🔄 По очереди** — игроки рисуют по очереди, создавая совместный арт
- **🪞 Зеркало** — синхронное рисование (в разработке)

### 🛠️ Инструменты
- 🖌️ Кисть
- 🧹 Ластик
- ⬜ Прямоугольник
- ⭕ Круг
- 📏 Линия
- 🎨 Палитра цветов
- 📏 Выбор размера кисти (S/M/L)

### 💬 Коммуникация
- Чат в реальном времени
- Системные уведомления
- Копирование кода комнаты

### 🎵 Дополнительно
- Фоновая музыка с кнопкой управления
- Сохранение состояния музыки
- Адаптивный дизайн для мобильных устройств

## 🚀 Быстрый старт

### Требования
- Python 3.10+
- PostgreSQL (опционально, по умолчанию SQLite)
- Redis (опционально, для production)

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/diogennpluq/pair_canvas_project.git
cd pair_canvas_project
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Выполните миграции:**
```bash
python manage.py migrate
```

5. **Соберите статические файлы:**
```bash
python manage.py collectstatic
```

6. **Запустите сервер разработки:**
```bash
python manage.py runserver
```

7. **Откройте браузер:**
```
http://127.0.0.1:8000/
```

## 📖 Использование

### Регистрация и вход
1. Зарегистрируйте аккаунт или войдите
2. Заполните профиль (аватар, био)

### Создание комнаты
1. Нажмите **"Создать комнату"**
2. Выберите режим рисования
3. Для режима "По очереди" укажите количество ходов
4. Скопируйте код комнаты и отправьте другу

### Присоединение к комнате
1. Нажмите **"Присоединиться"**
2. Введите код комнаты
3. Начните рисовать вместе!

### Рисование
- Выберите инструмент на панели
- Выберите цвет в палитре
- Рисуйте на холсте
- Используйте **Undo/Redo** для отмены действий
- Нажмите **"Сохранить"** для скачивания рисунка

## 🏗️ Архитектура проекта

```
pair_canvas_project/
├── accounts/           # Приложение пользователей
│   ├── models.py      # Кастомная модель CustomUser
│   ├── views.py       # Регистрация, профиль
│   └── forms.py       # Формы регистрации
├── rooms/             # Приложение комнат
│   ├── models.py      # Room, ChatMessage, Drawing
│   ├── consumers.py   # WebSocket обработчики
│   ├── api_views.py   # REST API endpoints
│   └── routing.py     # WebSocket роутинг
├── gallery/           # Галерея рисунков
├── templates/         # HTML шаблоны
├── static/           # Статические файлы
│   └── audio/        # Фоновая музыка
└── pair_canvas/      # Настройки проекта
    ├── settings.py
    ├── urls.py
    └── asgi.py       # ASGI конфигурация
```

## 🔧 Технологии

| Технология | Назначение |
|------------|------------|
| **Django 5.0+** | Backend фреймворк |
| **Django Channels** | WebSocket поддержка |
| **Daphne** | ASGI сервер |
| **HTML5 Canvas** | Рисование на холсте |
| **JavaScript** | Клиентская логика |
| **SQLite/PostgreSQL** | База данных |
| **Redis** | Канальный слой (production) |

## ⚙️ Настройки

### Переменные окружения (опционально)

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# База данных (для production)
DATABASE_URL=postgresql://user:password@localhost:5432/pair_canvas

# Redis (для production)
REDIS_URL=redis://localhost:6379/0
```

### Настройка Channels

Для production измените `CHANNEL_LAYERS` в `settings.py`:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis://127.0.0.1:6379/1")],
        },
    },
}
```

## 🧪 Тестирование

Запуск тестов:

```bash
python manage.py test
```

Покрытие: **59 тестов**
- Тесты моделей
- Тесты представлений
- Тесты API
- Тесты режимов рисования

## 📝 API Endpoints

### Комнаты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/check_room/<code>/` | Проверка комнаты |
| POST | `/api/join_room_api/` | Присоединиться |
| POST | `/api/leave_room_api/<code>/` | Покинуть комнату |
| GET | `/api/get_messages/<code>/` | История чата |
| GET | `/api/get_state/<code>/` | Состояние комнаты |
| POST | `/api/next_turn/<code>/` | Следующий ход |

### WebSocket

Подключение: `ws://host/ws/room/<room_code>/`

**Типы сообщений:**
- `chat_message` — сообщение в чат
- `drawing` — данные рисования
- `clear_canvas` — очистка холста
- `tool_change` — смена инструмента
- `game_state_update` — обновление состояния игры

## 🎨 Режимы рисования

### Свободное рисование
Оба участника могут рисовать одновременно. Идеально для совместного творчества.

### По очереди
Игроки рисуют по очереди. Каждый ход создаёт элемент рисунка.

**Настройки:**
- Количество ходов (1-20)
- Определение текущего рисующего
- Уведомления о смене хода

## 📱 Адаптивность

Приложение полностью адаптировано для:
- 📱 iPhone и Android
- 📱 Планшетов
- 💻 Десктопов
- 🖥️ Сенсорных устройств

## 🔐 Безопасность

- ✅ CSRF защита
- ✅ Аутентификация пользователей
- ✅ Уникальные email
- ✅ Хэширование паролей
- ✅ Валидация данных
- ✅ Защита от XSS

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 👥 Авторы

- **diogennpluq** — *Основная разработка*

## 🙏 Благодарности

- Django Community
- Channels Team
- Всем контрибьюторам

## 📞 Контакты

- GitHub: [@diogennpluq](https://github.com/diogennpluq)
- Проект: [Pair Canvas](https://github.com/diogennpluq/pair_canvas_project)

---

<div align="center">

**🎨 Рисуйте вместе с Pair Canvas!**

[Наверх](#-pair-canvas---совместное-рисование-в-реальном-времени)

</div>
