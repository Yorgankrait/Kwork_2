import os
from django.core.management.base import BaseCommand
from django.conf import settings
from smeta.models import LogFile


class Command(BaseCommand):
    help = 'Сканирует директорию логов и обновляет базу данных'

    def handle(self, *args, **kwargs):
        log_dir = settings.LOG_DIR
        existing_logs = set(LogFile.objects.values_list('file_name', flat=True))
        current_logs = {f for f in os.listdir(log_dir) if f.endswith('.log') or f.endswith('.log.')}

        new_logs = current_logs - existing_logs
        for log_file in new_logs:
            LogFile.objects.create(file_name=log_file)

        self.stdout.write(self.style.SUCCESS(f'Добавлено {len(new_logs)} новых логов'))

