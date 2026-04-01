from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rooms.models import Drawing
import os


class Command(BaseCommand):
    help = 'Очистка старых рисунков для освобождения места'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Количество дней для хранения рисунков (по умолчанию 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать какие рисунки будут удалены, но не удалять их'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timedelta(days=days)
        old_drawings = Drawing.objects.filter(created_at__lt=cutoff_date)

        count = old_drawings.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'Нет рисунков старше {days} дней')
            )
            return

        self.stdout.write(f'Найдено {count} рисунков старше {days} дней:')

        for drawing in old_drawings:
            self.stdout.write(f'  - Рисунок #{drawing.id} от {drawing.created_at} (комната {drawing.room.code})')

            if not dry_run:
                # Удаляем файл изображения
                if drawing.image:
                    if os.path.isfile(drawing.image.path):
                        os.remove(drawing.image.path)
                drawing.delete()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDry run: {count} рисунков готовы к удалению. '
                    'Запустите без --dry-run для фактического удаления.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nУдалено {count} старых рисунков')
            )
