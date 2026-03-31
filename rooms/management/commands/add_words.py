from django.core.management.base import BaseCommand
from rooms.models import Word

class Command(BaseCommand):
    help = 'Добавляет слова для режима "Угадай рисунок"'

    def handle(self, *args, **kwargs):
        words = [
            # Лёгкие
            {'word': 'кот', 'category': 'Животные', 'difficulty': 'easy'},
            {'word': 'дом', 'category': 'Здания', 'difficulty': 'easy'},
            {'word': 'солнце', 'category': 'Природа', 'difficulty': 'easy'},
            {'word': 'дерево', 'category': 'Природа', 'difficulty': 'easy'},
            {'word': 'машина', 'category': 'Транспорт', 'difficulty': 'easy'},
            {'word': 'цветок', 'category': 'Природа', 'difficulty': 'easy'},
            {'word': 'книга', 'category': 'Предметы', 'difficulty': 'easy'},
            {'word': 'мяч', 'category': 'Спорт', 'difficulty': 'easy'},
            {'word': 'рыба', 'category': 'Животные', 'difficulty': 'easy'},
            {'word': 'птица', 'category': 'Животные', 'difficulty': 'easy'},
            
            # Средние
            {'word': 'велосипед', 'category': 'Транспорт', 'difficulty': 'medium'},
            {'word': 'самолёт', 'category': 'Транспорт', 'difficulty': 'medium'},
            {'word': 'динозавр', 'category': 'Животные', 'difficulty': 'medium'},
            {'word': 'робот', 'category': 'Техника', 'difficulty': 'medium'},
            {'word': 'пицца', 'category': 'Еда', 'difficulty': 'medium'},
            {'word': 'гитара', 'category': 'Музыка', 'difficulty': 'medium'},
            {'word': 'телефон', 'category': 'Техника', 'difficulty': 'medium'},
            {'word': 'чемодан', 'category': 'Предметы', 'difficulty': 'medium'},
            {'word': 'фонарь', 'category': 'Предметы', 'difficulty': 'medium'},
            {'word': 'корабль', 'category': 'Транспорт', 'difficulty': 'medium'},
            
            # Сложные
            {'word': 'космонавт', 'category': 'Профессии', 'difficulty': 'hard'},
            {'word': 'вулкан', 'category': 'Природа', 'difficulty': 'hard'},
            {'word': 'лабиринт', 'category': 'Предметы', 'difficulty': 'hard'},
            {'word': 'фейерверк', 'category': 'Развлечения', 'difficulty': 'hard'},
            {'word': 'аквариум', 'category': 'Предметы', 'difficulty': 'hard'},
            {'word': 'бумеранг', 'category': 'Предметы', 'difficulty': 'hard'},
            {'word': 'карусель', 'category': 'Развлечения', 'difficulty': 'hard'},
            {'word': 'подводная лодка', 'category': 'Транспорт', 'difficulty': 'hard'},
            {'word': 'небоскрёб', 'category': 'Здания', 'difficulty': 'hard'},
            {'word': 'холодильник', 'category': 'Предметы', 'difficulty': 'hard'},
        ]

        for w in words:
            Word.objects.get_or_create(
                word=w['word'],
                defaults={'category': w['category'], 'difficulty': w['difficulty']}
            )

        self.stdout.write(self.style.SUCCESS(f'Добавлено {len(words)} слов'))
