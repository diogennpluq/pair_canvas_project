from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание администратора Pair Canvas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя администратора (по умолчанию: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@paircanvas.com',
            help='Email администратора (по умолчанию: admin@paircanvas.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Пароль администратора (по умолчанию: admin123)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Пользователь {username} уже существует')
            )
            admin = User.objects.get(username=username)
            if not admin.is_staff:
                admin.is_staff = True
                admin.is_superuser = True
                admin.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Пользователь {username} назначен администратором')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'{username} уже является администратором')
                )
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Администратор {username} успешно создан!\n'
                    f'📧 Email: {email}\n'
                    f'🔑 Пароль: {password}\n\n'
                    f'Войдите в админку: /admin/'
                )
            )
