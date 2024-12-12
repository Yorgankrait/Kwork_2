# custom_filters.py
from django import template

register = template.Library()

@register.filter
def currency(value):
    # Преобразуем значение в строку с разделением тысяч пробелами и добавляем символ ₽
    return f"{value:,.0f} ₽".replace(",", " ")
