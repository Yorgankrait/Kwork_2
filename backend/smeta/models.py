from django.db import models
from django.core.validators import FileExtensionValidator
import uuid
import random
from django.utils.timezone import now
import os
from django.conf import settings


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
    handles = models.CharField(max_length=255, verbose_name='Ручки', null=True, blank=True)
    options = models.ManyToManyField(Option, related_name='products', verbose_name='Опции', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    image = models.TextField(verbose_name='Изображение') # base64 image storage
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость', default=0)

    class Meta:
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'

    def __str__(self):
        return f'{self.system} {self.series}'

class Additional(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Доп. Изделие'
        verbose_name_plural = 'Доп. Изделия'

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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='Уникальный UUID')
    number = models.CharField(max_length=50, verbose_name='Номер')
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='order', verbose_name='Офис')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='order', verbose_name='Менеджер')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена старая')
    new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена новая')
    products = models.ManyToManyField(Product, related_name='orders', verbose_name='Изделия')
    additionals = models.ManyToManyField(Additional, related_name='orders', verbose_name='Дополнительные', blank=True)
    services = models.ManyToManyField(Service, related_name='orders', verbose_name='Услуги', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_pdf = models.FileField(
        upload_to='media/pdf/',
        blank=True,
        null=True,
        verbose_name='PDF сметы',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    code = models.CharField(max_length=4, blank=True, verbose_name='Код')

    def generate_code(self):
        return ''.join(random.choices('0123456789', k=4))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

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


class LogFile(models.Model):
    file_name = models.CharField(max_length=255, unique=True, verbose_name='Название файла')
    created_at = models.DateTimeField(default=now, verbose_name='Дата создания')

    def file_path(self):
        return os.path.join(settings.LOG_DIR, self.file_name)

    def save(self, *args, **kwargs):
        """При сохранении создаем файл, если он не существует"""
        is_new = self.pk is None  # Проверяем, новый ли объект
        
        # Сохраняем объект в базу данных
        super().save(*args, **kwargs)
        
        # Если это новая запись и файл не существует, создаем его
        if is_new:
            file_path = self.file_path()
            if not os.path.exists(file_path):
                try:
                    # Создаем директорию, если её нет
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    # Создаем пустой файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Лог-файл {self.file_name}, создан автоматически {now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                except Exception as e:
                    import logging
                    logger = logging.getLogger('django')
                    logger.error(f"Ошибка при создании лог-файла {self.file_name}: {str(e)}")

    def delete(self, *args, **kwargs):
        """При удалении из БД удаляем файл с диска"""
        try:
            os.remove(self.file_path())
        except FileNotFoundError:
            pass
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'


class ChatCode(models.Model):
    code = models.TextField(null=True, blank=True, verbose_name='Код чата')

    def __str__(self):
        return 'Код чата'

    class Meta:
            verbose_name = 'Код чата'
            verbose_name_plural = 'Код чата'


class AnalyticsCode(models.Model):
    code = models.TextField(null=True, blank=True, verbose_name='Код аналитики')

    def __str__(self):
        return 'Код метрик'

    class Meta:
        verbose_name = 'Код метрики'
        verbose_name_plural = 'Код метрики'


class RawJSON(models.Model):
    """Модель для хранения оригинального JSON"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='raw_json', verbose_name='Заказ')
    data = models.JSONField(verbose_name='Исходный JSON')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Исходный JSON'
        verbose_name_plural = 'Исходные JSON'

    def __str__(self):
        return f'JSON для заказа {self.order.number}'


class ScriptCode(models.Model):
    """Модель для хранения скриптов с указанием места размещения"""
    PLACEMENT_CHOICES = [
        ('head_start', 'В начале head'),
        ('head_end', 'В конце head'),
        ('body_start', 'В начале body'),
        ('body_end', 'В конце body'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    code = models.TextField(verbose_name='Код скрипта')
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, verbose_name='Место размещения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Скрипт'
        verbose_name_plural = 'Скрипты'
        
    def __str__(self):
        return self.name


class WebhookSettings(models.Model):
    """Модель для хранения настроек вебхука"""
    url = models.URLField(verbose_name='URL вебхука')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = 'Настройка вебхука'
        verbose_name_plural = 'Настройки вебхука'
        
    def __str__(self):
        return self.url


class TemplateSettings(models.Model):
    """Модель для хранения шаблона сметы"""
    name = models.CharField(max_length=255, verbose_name='Название')
    html_template = models.TextField(verbose_name='HTML шаблон')
    css_template = models.TextField(verbose_name='CSS шаблон')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Шаблон сметы'
        verbose_name_plural = 'Шаблоны сметы'
        
    def __str__(self):
        return self.name


class LogSettings(models.Model):
    """Модель для настройки хранения логов"""
    retention_days = models.PositiveIntegerField(default=30, verbose_name='Срок хранения (дней)')
    
    class Meta:
        verbose_name = 'Настройка логирования'
        verbose_name_plural = 'Настройки логирования'
        
    def __str__(self):
        return f'Хранить логи {self.retention_days} дней'


class LogKeyword(models.Model):
    """Модель для хранения ключевых слов для фильтрации логов"""
    keyword = models.CharField(max_length=255, unique=True, verbose_name='Ключевое слово')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='Количество использований')
    
    def __str__(self):
        return self.keyword
    
    class Meta:
        verbose_name = 'Ключевое слово лога'
        verbose_name_plural = 'Ключевые слова логов'
        ordering = ['-usage_count', 'keyword']


class LogFilter(models.Model):
    """Модель для фильтрации логов по ключевым словам и уровню"""
    name = models.CharField(max_length=255, verbose_name='Название фильтра')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    keywords = models.ManyToManyField(LogKeyword, blank=True, related_name='filters', verbose_name='Ключевые слова')
    log_level = models.CharField(
        max_length=20,
        choices=[
            ('ALL', 'Все уровни'),
            ('INFO', 'Информация'),
            ('WARNING', 'Предупреждения'),
            ('ERROR', 'Ошибки'),
            ('DEBUG', 'Отладка'),
        ],
        default='ALL',
        verbose_name='Уровень логов'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Фильтр логов'
        verbose_name_plural = 'Фильтры логов'

