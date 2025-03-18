import os
import logging
import requests
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Order, LogFile, LogSettings
from django.utils import timezone

logger = logging.getLogger('django')

@shared_task
def save_pdf_to_order(order_id, pdf_content, file_name):
    """
    Сохраняет PDF файл к заказу.
    """
    try:
        order = Order.objects.get(id=order_id)
        content_file = ContentFile(pdf_content)
        order.order_pdf.save(file_name, content_file, save=True)
        logger.info(f"PDF успешно сохранен для заказа {order.number}")
        return True
    except Order.DoesNotExist:
        logger.error(f"Заказ с ID {order_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка при сохранении PDF для заказа {order_id}: {str(e)}")
        return False

@shared_task
def delete_old_logs_task():
    """
    Удаляет старые логи в соответствии с настройками хранения.
    """
    try:
        # Получаем настройки хранения логов
        log_settings = LogSettings.objects.first()
        retention_days = 30  # значение по умолчанию
        
        # Если настройки существуют, используем их
        if log_settings:
            retention_days = log_settings.retention_days
            
        # Вычисляем дату, до которой нужно удалить логи
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Получаем список старых логов
        old_logs = LogFile.objects.filter(created_at__lt=cutoff_date)
        
        log_count = old_logs.count()
        if log_count > 0:
            # Удаляем старые логи
            old_logs.delete()
            logger.info(f"Удалено {log_count} старых логов (старше {retention_days} дней)")
        else:
            logger.info(f"Нет логов старше {retention_days} дней для удаления")
            
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении старых логов: {str(e)}")
        return False

@shared_task
def scan_logs_task():
    """
    Сканирует директорию с логами и добавляет файлы в БД, если их там нет.
    """
    try:
        # Проверяем существование директории
        if not os.path.exists(settings.LOG_DIR):
            os.makedirs(settings.LOG_DIR)
            logger.info(f"Создана директория для логов: {settings.LOG_DIR}")
            
        # Получаем список файлов в директории
        log_files = [f for f in os.listdir(settings.LOG_DIR) if os.path.isfile(os.path.join(settings.LOG_DIR, f))]
        
        # Список файлов в базе данных
        db_files = set(LogFile.objects.values_list('file_name', flat=True))
        
        # Добавляем файлы, которых нет в БД
        added_count = 0
        for file_name in log_files:
            if file_name not in db_files:
                LogFile.objects.create(file_name=file_name)
                added_count += 1
                
        if added_count > 0:
            logger.info(f"Добавлено {added_count} новых файлов логов в базу данных")
        else:
            logger.info("Новых файлов логов не обнаружено")
            
        return True
    except Exception as e:
        logger.error(f"Ошибка при сканировании директории логов: {str(e)}")
        return False

@shared_task
def send_webhook(webhook_url, data):
    """
    Отправляет данные на указанный вебхук URL.
    """
    try:
        # Добавляем timestamp
        data['timestamp'] = timezone.now().isoformat()
        
        # Отправляем POST запрос
        response = requests.post(webhook_url, json=data, timeout=10)
        
        # Проверяем статус ответа
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Вебхук успешно отправлен на {webhook_url}, статус: {response.status_code}")
            return True
        else:
            logger.warning(f"Вебхук отправлен с ошибкой на {webhook_url}, статус: {response.status_code}, ответ: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Ошибка при отправке вебхука на {webhook_url}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Необработанная ошибка при отправке вебхука: {str(e)}")
        return False

