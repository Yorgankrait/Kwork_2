import os
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from smeta.models import LogFile

class Command(BaseCommand):
    help = 'Удаляет старые логи старше 30 дней'

    def handle(self, *args, **kwargs):
        threshold_date = now() - timedelta(days=30)
        old_logs = LogFile.objects.filter(created_at__lt=threshold_date)

        for log in old_logs:
            log.delete()

        self.stdout.write(self.style.SUCCESS(f'Удалено {old_logs.count()} старых логов'))

