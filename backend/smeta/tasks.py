from celery import shared_task
from .services import generate_and_write_pdf
from django.core.exceptions import ValidationError
from django.conf import settings


@shared_task
def generate_pdf_task(smeta_id):
    from .models import Order  # Импортировать модель внутри функции для избежания циклических импортов
    try:
        smeta = Order.objects.get(id=smeta_id)
        generate_and_write_pdf(settings.SITE_URL, smeta)
        return f"PDF успешно создан для сметы {smeta.number}"
    except Order.DoesNotExist:
        raise ValidationError("Смета не найдена")
    except Exception as e:
        raise ValidationError(f"Ошибка при создании PDF: {str(e)}")
