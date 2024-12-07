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