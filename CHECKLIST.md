# 🚀 Production Checklist для Pair Canvas

## ✅ Выполненные задачи

### Баги исправлены
- [x] Музыка из `/static/audio` - переименован файл, исправлен путь
- [x] Дублирование сообщений в чате - убрано локальное добавление
- [x] Удаление рисунка кисточкой при рисовании фигур - исправлено в `handleRemoteDrawing`
- [x] Кнопка "Отменить" - теперь отправляет `undo_action` вместо `clear_canvas`
- [x] Сохранение состояния музыки между страницами - localStorage + автозапуск

### Галерея рисунков
- [x] Модель Drawing обновлена (поле `image` для файлов)
- [x] API endpoint `/api/save_drawing/<room_code>/` для сохранения
- [x] Шаблон галереи обновлён для отображения изображений
- [x] Migration создана и применена

### Production настройки
- [x] `settings_prod.py` с безопасными настройками
- [x] `.env.example` с примером переменных
- [x] `.env` для development
- [x] `requirements.txt` обновлён
- [x] WhiteNoise для статических файлов
- [x] Логгирование настроено

### Docker и деплой
- [x] `Dockerfile` для приложения
- [x] `docker-compose.yml` (PostgreSQL, Redis, Web, Nginx)
- [x] `nginx.conf` с SSL и rate limiting
- [x] `deploy.sh` скрипт развёртывания
- [x] `backup.sh` скрипт бэкапа
- [x] `setup_ssl.sh` для SSL сертификатов
- [x] `.dockerignore`

### CI/CD
- [x] GitHub Actions workflow (`.github/workflows/ci-cd.yml`)
- [x] Тестирование, сборка, деплой

### Утилиты
- [x] `generate_secret_key.sh` - генерация SECRET_KEY
- [x] `cleanup_old_drawings.py` - очистка старых рисунков
- [x] `.pre-commit-config.yaml` - pre-commit хуки

### Документация
- [x] `README.md` обновлён
- [x] `README_PRODUCTION.md` - полная инструкция по production
- [x] `CHECKLIST.md` - этот файл

## 📋 Шаги для развёртывания в production

### 1. Подготовка сервера

```bash
# Установите Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установите git
apt update && apt install -y git
```

### 2. Клонирование проекта

```bash
git clone <your-repo-url>
cd pair_canvas_project
```

### 3. Настройка окружения

```bash
# Скопируйте пример
cp .env.example .env

# Сгенерируйте SECRET_KEY
chmod +x generate_secret_key.sh
./generate_secret_key.sh

# Отредактируйте .env
nano .env
```

### 4. Настройка SSL

```bash
# Для development (self-signed)
chmod +x setup_ssl.sh
./setup_ssl.sh yourdomain.com your@email.com

# Для production (Let's Encrypt)
# Раскомментируйте certbot в docker-compose.yml
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email your@email.com --agree-tos --no-eff-email -d yourdomain.com
```

### 5. Запуск

```bash
chmod +x deploy.sh
./deploy.sh
```

### 6. Проверка

```bash
# Статус сервисов
docker-compose ps

# Логи
docker-compose logs -f web
docker-compose logs -f nginx

# Проверка доступности
curl -I http://localhost:8000
```

### 7. Создание суперпользователя

```bash
docker-compose run --rm web python manage.py createsuperuser
```

## 🔒 Security Checklist

- [ ] Измените `SECRET_KEY` на уникальный
- [ ] Установите `DEBUG=False`
- [ ] Настройте `ALLOWED_HOSTS`
- [ ] Используйте HTTPS в production
- [ ] Настройте firewall (только 80, 443, 22)
- [ ] Регулярно обновляйте зависимости
- [ ] Настройте бэкапы базы данных
- [ ] Используйте надёжные пароли

## 📊 Мониторинг

```bash
# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f

# Проверка ошибок
docker-compose logs web | grep ERROR

# Размер базы данных
docker-compose exec db psql -U pair_canvas -c "SELECT pg_size_pretty(pg_database_size('pair_canvas'));"
```

## 🧹 Обслуживание

### Еженедельно
```bash
# Очистка старых рисунков
docker-compose run --rm web python manage.py cleanup_old_drawings --days 30

# Очистка unused Docker ресурсов
docker system prune -af
```

### Ежемесячно
```bash
# Бэкап
./backup.sh

# Обновление зависимостей
pip install --upgrade -r requirements.txt
```

## 🆘 Troubleshooting

### Ошибка подключения к базе данных
```bash
docker-compose restart db
docker-compose logs db
```

### Ошибка WebSocket
```bash
docker-compose restart redis
docker-compose logs redis
```

### Проблемы со статикой
```bash
docker-compose run --rm web python manage.py collectstatic --clear --noinput
docker-compose restart nginx
```

### Приложение не запускается
```bash
# Проверьте логи
docker-compose logs web

# Проверьте переменные окружения
docker-compose config
```

## 📞 Поддержка

- GitHub Issues: https://github.com/diogennpluq/pair_canvas_project/issues
- Документация: README_PRODUCTION.md
