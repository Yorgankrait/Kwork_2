import uuid


def transform_keys(data):
    """
    Заменяет ключи в словаре или списке словарей по заданным правилам
    """

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


def get_or_create_user_id(request):
    """
    Создает или получает UUID пользователя

    - в дальнейшем UUID сохраняется в COOKIES для идентификации пользователя
    """
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())

    return user_id
