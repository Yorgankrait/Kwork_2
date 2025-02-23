from celery import shared_task
from django.core.files.base import ContentFile


@shared_task
def save_pdf_to_order(order_id, file_data, file_name):
    """
    Задача для сохранения PDF файла в модель Order.
    :param order_id: ID заказа.
    :param file_data: Содержимое файла в байтах.
    :param file_name: Имя файла.
    """
    from .models import Order  # Импортируем здесь, чтобы избежать циклических импортов

    try:
        order = Order.objects.get(id=order_id)
        order.order_pdf.save(file_name, ContentFile(file_data))
        order.save()
        return f"PDF файл успешно сохранен для заказа {order_id}"
    except Order.DoesNotExist:
        return f"Заказ с ID {order_id} не найден"

@shared_task
def scan_logs_task():
    call_command('scan_logs')

@shared_task
def delete_old_logs_task():
    call_command('delete_old_logs')

