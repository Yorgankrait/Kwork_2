from django import template
from django.template import Template, Context

register = template.Library()

@register.filter
def process_template_string(value, arg):
    """
    Обрабатывает строку шаблона с контекстом.
    Использование: {{ template_string|process_template_string:context_dict }}
    """
    if not value:
        return ""
    try:
        template = Template(value)
        context = Context(arg)
        return template.render(context)
    except Exception as e:
        return f"Ошибка обработки шаблона: {str(e)}" 