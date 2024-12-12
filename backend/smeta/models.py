from django.db import models
from django.core.validators import FileExtensionValidator


class Office(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Офис'
        verbose_name_plural = 'Офисы'

    def __str__(self):
        return str(self.name)

class Manager(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

    def __str__(self):
        return str(self.name)

class Option(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'Опция'
        verbose_name_plural = 'Опции'

    def __str__(self):
        return str(self.name)

class Product(models.Model):
    identifier = models.IntegerField(verbose_name='Идентификатор')
    system = models.CharField(max_length=255, verbose_name='Система')
    series = models.CharField(max_length=255, verbose_name='Серия', null=True, blank=True)
    width = models.PositiveIntegerField(verbose_name='Ширина')
    height = models.PositiveIntegerField(verbose_name='Высота')
    base_color = models.CharField(max_length=255, verbose_name='Цвет основания')
    inner_color = models.CharField(max_length=255, verbose_name='Цвет внутренний')
    outer_color = models.CharField(max_length=255, verbose_name='Цвет внешний')
    handles = models.CharField(max_length=255, verbose_name='Ручки')
    options = models.ManyToManyField(Option, related_name='products', verbose_name='Опции')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    image = models.TextField(verbose_name='Изображение')  # Assuming base64 image storage

    class Meta:
        verbose_name = 'Издение'
        verbose_name_plural = 'Изделия'

    def __str__(self):
        return f'{self.system} {self.series}'

class Additional(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Дополнительный'
        verbose_name_plural = 'Дополнительные'

    def __str__(self):
        return str(self.name)

class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return str(self.name)

class Order(models.Model):
    number = models.CharField(max_length=50, verbose_name='Номер', unique=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='order', verbose_name='Офис')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='order', verbose_name='Менеджер')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена старая')
    new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена новая')
    products = models.ManyToManyField(Product, related_name='orders', verbose_name='Изделия')
    additionals = models.ManyToManyField(Additional, related_name='orders', verbose_name='Дополнительные')
    services = models.ManyToManyField(Service, related_name='orders', verbose_name='Услуги')
    order_pdf = models.FileField(
        upload_to='media/pdf/',
        blank=True,
        null=True,
        verbose_name='PDF сметы',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    class Meta:
        verbose_name = 'Смета | Заказ'
        verbose_name_plural = 'Сметы | Заказы'

    def __str__(self):
        return str(self.number)

class OrderRating(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ratings', verbose_name='Смета / Заказ')
    user_id = models.UUIDField(verbose_name='Уникальный идентификатор пользователя')
    liked = models.BooleanField(verbose_name='Оценка: Нрав./Не нрав.')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата-Время создания')

    class Meta:
        verbose_name = 'Оценка - Сметы | Заказа'
        verbose_name_plural = 'Оценки - Сметы | Заказа'

    def __str__(self):
        return f'{self.order.number} | {"Нравится" if self.liked else "Не нравится"}'
