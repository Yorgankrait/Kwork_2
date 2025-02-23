# custom_filters.py
from django import template
import re
from datetime import datetime

register = template.Library()


@register.filter
def currency(value):
    # Преобразуем значение в строку с разделением тысяч пробелами и добавляем символ ₽
    return f"{value:,.0f} ₽".replace(",", " ")

@register.filter
def format_phone(value):
    """Форматирование номера телефона в формат +7 (495) 660-70-15"""
    digits = re.sub(r'\D', '', value)  # Удаляем все нецифровые символы
    if len(digits) == 11 and digits.startswith('7'):
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    return value  # Возвращаем как есть, если формат не подходит

@register.filter
def format_date_custom(value):
    """
    Форматирует дату в формат YYYMMDDD.
    """
    if not value:
        return ""

    try:
        # Преобразуем значение в datetime, если это строка
        if isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%d")

        # Форматируем дату
        year = value.strftime('%y')  # Последние две цифры года
        month = value.strftime('%m')  # Месяц
        day = value.strftime('%d')    # День

        return f"{year}{month}{day}"
    except Exception as e:
        return str(e)  # В случае ошибки вернем сообщение об ошибке

