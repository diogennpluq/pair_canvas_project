# Production README

## Быстрый старт для продакшена

### Требования
- Docker и Docker Compose
- Доменное имя (для SSL)
- PostgreSQL (включен в docker-compose)
- Redis (включен в docker-compose)

### Установка

1. **Склонируйте репозиторий:**
```bash
git clone <repository-url>
cd pair_canvas_project
```

2. **Создайте файл окружения:**
```bash
cp .env.example .env
```

3. **Сгенерируйте SECRET_KEY:**
```bash
chmod +x generate_secret_key.sh
./generate_secret_key.sh
```
Скопируйте полученный ключ в `.env` файл.

4. **Настройте переменные окружения:**
Отредактируйте `.env` файл, установив:
- `SECRET_KEY` - сгенерированный ключ
- `POSTGRES_PASSWORD` - надёжный пароль для БД
- `ALLOWED_HOSTS` - ваш домен
- `EMAIL_HOST_USER` и `EMAIL_HOST_PASSWORD` - для уведомлений

5. **Настройте SSL (для production):**
```bash
chmod +x setup_ssl.sh
./setup_ssl.sh yourdomain.com your@email.com
```

Для Let's Encrypt в production:
```bash
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email your@email.com --agree-tos --no-eff-email -d yourdomain.com
```

6. **Запустите проект:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Проверка статуса

```bash
# Статус сервисов
docker-compose ps

# Логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web
```

### Остановка

```bash
docker-compose down
```

### Обновление

```bash
git pull
docker-compose build
docker-compose up -d
```

### База данных

```bash
# Миграции
docker-compose run --rm web python manage.py migrate

# Создание суперпользователя
docker-compose run --rm web python manage.py createsuperuser

# Бэкап базы данных
docker-compose exec db pg_dump -U pair_canvas pair_canvas > backup.sql

# Восстановление из бэкапа
cat backup.sql | docker-compose exec -T db psql -U pair_canvas pair_canvas
```

### Статические файлы

```bash
# Сборка статических файлов
docker-compose run --rm web python manage.py collectstatic --noinput

# Очистка старых файлов
docker-compose run --rm web python manage.py collectstatic --clear
```

### Мониторинг

```bash
# Использование ресурсов
docker stats

# Проверка логов на ошибки
docker-compose logs web | grep ERROR

# Проверка доступности
curl -I http://localhost:8000
```

### Troubleshooting

**Ошибка подключения к базе данных:**
```bash
docker-compose restart db
docker-compose logs db
```

**Ошибка WebSocket:**
```bash
docker-compose logs redis
docker-compose restart redis
```

**Проблемы со статическими файлами:**
```bash
docker-compose run --rm web python manage.py collectstatic --clear --noinput
docker-compose restart nginx
```

### Безопасность

1. Регулярно обновляйте зависимости:
```bash
pip install --upgrade -r requirements.txt
```

2. Используйте HTTPS в production
3. Настройте firewall (только порты 80, 443, 22)
4. Регулярно делайте бэкапы базы данных
5. Используйте надёжные пароли

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `SECRET_KEY` | Ключ безопасности Django | `django-insecure-...` |
| `DEBUG` | Режим отладки | `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `example.com,www.example.com` |
| `POSTGRES_DB` | Имя базы данных | `pair_canvas` |
| `POSTGRES_USER` | Пользователь БД | `pair_canvas` |
| `POSTGRES_PASSWORD` | Пароль БД | `change_this_password` |
| `POSTGRES_HOST` | Хост БД | `db` |
| `POSTGRES_PORT` | Порт БД | `5432` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/1` |
| `EMAIL_HOST_USER` | Email для уведомлений | `noreply@example.com` |
| `EMAIL_HOST_PASSWORD` | Пароль email | `app-password` |
| `SECURE_SSL_REDIRECT` | Перенаправление на HTTPS | `True` |

### Поддержка

Для создания issue используйте GitHub Issues.
