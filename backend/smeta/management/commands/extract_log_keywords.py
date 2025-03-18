import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from smeta.models import LogKeyword

# Регулярные выражения для извлечения важных частей сообщений логов
PATTERNS = [
    r'UUID[\s:]*([a-f0-9-]+)',  # UUID
    r'Создана смета',  # Создание сметы
    r'Обработка вебхука',  # Вебхуки
    r'webhook',  # Вебхуки (англ.)
    r'вебхук',  # Вебхуки (рус.)
    r'Ошибка',  # Ошибки
    r'Error',  # Ошибки (англ.)
    r'Exception',  # Исключения
    r'Запрос к API',  # API запросы
    r'шаблон',  # Работа с шаблонами
    r'Отправка email',  # Email сообщения
    r'export',  # Экспорт
    r'import',  # Импорт
    r'авторизац',  # Авторизация
    r'пользовател',  # Пользователи
    r'админ',  # Админ-панель
]

class Command(BaseCommand):
    help = 'Извлекает ключевые слова из файлов логов и добавляет их в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            help='Удаляет существующие ключевые слова перед извлечением',
        )

    def handle(self, *args, **options):
        if options['reset']:
            LogKeyword.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Существующие ключевые слова удалены'))

        log_path = os.path.join(settings.LOG_DIR, 'app.log')
        if not os.path.exists(log_path):
            self.stdout.write(self.style.ERROR(f'Файл логов не найден: {log_path}'))
            return

        # Извлекаем предопределенные ключевые слова
        self.extract_predefined_keywords()
        
        # Извлекаем ключевые слова из файла логов
        self.extract_keywords_from_log(log_path)
        
        # Выводим результаты
        keyword_count = LogKeyword.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Обработка завершена. Всего ключевых слов: {keyword_count}'))

    def extract_predefined_keywords(self):
        """Добавляет предопределенные ключевые слова"""
        predefined = [
            ('UUID', 'Идентификаторы UUID смет и других объектов'),
            ('Создана смета', 'Сообщения о создании новых смет'),
            ('Обработка вебхука', 'Логи обработки входящих вебхуков'),
            ('webhook', 'Логи связанные с вебхуками (англ.)'),
            ('вебхук', 'Логи связанные с вебхуками (рус.)'),
            ('Ошибка', 'Сообщения об ошибках'),
            ('Error', 'Сообщения об ошибках (англ.)'),
            ('Exception', 'Исключения в приложении'),
            ('Запрос к API', 'Логи внешних API-запросов'),
            ('шаблон', 'Работа с шаблонами'),
            ('Отправка email', 'Логи отправки электронных писем'),
            ('export', 'Экспорт данных'),
            ('import', 'Импорт данных'),
            ('авторизация', 'Авторизация пользователей'),
            ('пользователь', 'Действия пользователей'),
            ('администратор', 'Действия администраторов'),
        ]
        
        for keyword, description in predefined:
            LogKeyword.objects.get_or_create(
                keyword=keyword,
                defaults={'description': description}
            )
        
        self.stdout.write(self.style.SUCCESS(f'Добавлено {len(predefined)} предопределенных ключевых слов'))

    def extract_keywords_from_log(self, log_path):
        """Извлекает ключевые слова из файла логов"""
        with open(log_path, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                
                # Извлекаем дополнительные часто встречающиеся слова из логов
                # (для случаев, которые не покрываются предопределенными шаблонами)
                words = re.findall(r'\b[A-Za-zА-Яа-я]{5,}\b', content)
                word_count = {}
                
                for word in words:
                    if word.lower() in word_count:
                        word_count[word.lower()] += 1
                    else:
                        word_count[word.lower()] = 1
                
                # Добавляем часто встречающиеся слова как ключевые слова
                for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:30]:
                    if len(word) > 5 and count > 10:  # Только слова длиннее 5 символов, встречающиеся более 10 раз
                        LogKeyword.objects.get_or_create(
                            keyword=word,
                            defaults={'description': f'Автоматически извлечено из логов (встречается {count} раз)'}
                        )
                
                self.stdout.write(self.style.SUCCESS('Ключевые слова извлечены из логов'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при чтении файла логов: {e}')) 