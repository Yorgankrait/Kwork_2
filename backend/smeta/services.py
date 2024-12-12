import os
import uuid

from django.conf import settings
from django.contrib.auth.views import ValidationError
from django.templatetags.static import static
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile

from weasyprint import HTML, CSS


def transform_keys(data):
    mapping = {
        "Номер": "number",
        "Офис": "office",
        "Наименование": "name",
        "Адрес": "address",
        "Менеджер": "manager",
        "Имя": "name",
        "Телефон": "phone",
        "Цена старая": "old_price",
        "Цена новая": "new_price",
        "Изделия": "products",
        "Идентификатор": "identifier",
        "Система": "system",
        "Серия": "series",
        "Ширина": "width",
        "Высота": "height",
        "Цвет основания": "base_color",
        "Цвет внутренний": "inner_color",
        "Цвет внешний": "outer_color",
        "Ручки": "handles",
        "Опции": "options",
        "Наименование": "name",
        "Количество": "quantity",
        "Изображение": "image",
        "Допы": "additionals",
        "Название": "name",
        "Стоимость": "cost",
        "Услуги": "services"
    }

    if isinstance(data, dict):
        return {mapping.get(key, key): transform_keys(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [transform_keys(item) for item in data]
    return data


def generate_and_write_pdf(base_url, smeta):
    """
    Генерирует PDF-файл для сметы и сохраняет его в файловой системе.
    """
    try:
        context = prepare_pdf_context(base_url, smeta)
        html_string = render_to_string('order_detail_pdf.html', context=context)
        css = load_pdf_styles()
        pdf_bytes = generate_pdf(html_string, css)
        pdf_file = save_pdf_to_disk(pdf_bytes, smeta.number)

        link_pdf_to_model(smeta, pdf_bytes, pdf_file)

        return smeta.order_pdf
    except Exception as e:
        raise ValidationError(f"Ошибка при создании PDF: {str(e)}")

def prepare_pdf_context(base_url, smeta):
    """
    Подготавливает контекст данных для рендеринга PDF.
    """
    total_additionals_cost = sum([additional.cost for additional in smeta.additionals.all()])
    total_services_cost = sum([service.cost for service in smeta.services.all()])

    return {
        'order': smeta,
        'office': smeta.office,
        'manager': smeta.manager,
        'products': smeta.products.all(),
        'additionals': smeta.additionals.all(),
        'services': smeta.services.all(),
        'total_additionals_cost': total_additionals_cost,
        'total_services_cost': total_services_cost,
        'header_logo_url': f"{base_url}{static('img/header-logo.svg')}",
        'footer_logo_url': f"{base_url}{static('img/footer-logo.svg')}",
    }

def load_pdf_styles(base_url = None):
    """
    Загружает CSS-файлы для оформления PDF.
    """
    css_files = [
        finders.find('css/styles.css'),
    ]
    # Используем абсолютные пути или URL
    return [CSS(filename=finders.find(css_file)) for css_file in css_files if finders.find(css_file)]

def generate_pdf(html_string, css):
    """
    Генерирует PDF-файл из HTML-строки и CSS.
    """
    html = HTML(string=html_string)
    return html.write_pdf(stylesheets=css)

def save_pdf_to_disk(pdf_bytes, smeta_number):
    """
    Сохраняет PDF-файл в файловую систему.
    """
    filename = f"smeta_{smeta_number}.pdf"
    folder_path = os.path.join(settings.MEDIA_ROOT, 'pdf')
    filepath = os.path.join(folder_path, filename)

    os.makedirs(folder_path, exist_ok=True)

    with open(filepath, 'wb') as pdf_file:
        pdf_file.write(pdf_bytes)

    return filepath

def link_pdf_to_model(smeta, pdf_bytes, filepath):
    """
    Связывает созданный PDF-файл с моделью.
    """
    filename = os.path.basename(filepath)
    smeta.order_pdf.save(filename, ContentFile(pdf_bytes))


def get_or_create_user_id(request):
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())

    return user_id
