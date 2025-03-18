from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
import os

from .models import (
    Office, Manager, Option, Product, Additional, Service, Order, OrderRating, 
    LogFile, ChatCode, AnalyticsCode, RawJSON, ScriptCode, WebhookSettings, 
    TemplateSettings, LogSettings, LogFilter, LogKeyword
)


class ProductInline(admin.TabularInline):
    model = Order.products.through
    fields = ('product',)

class AdditionalInline(admin.TabularInline):
    model = Order.additionals.through
    extra = 1
    fields = ('additional',)

class ServiceInline(admin.TabularInline):
    model = Order.services.through
    extra = 1
    fields = ('service',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'number', 'code', 'office', 'manager', 'old_price', 'new_price')
    search_fields = ('number', 'office__name', 'manager__name')
    inlines = [ProductInline, AdditionalInline, ServiceInline]

    def delete_model(self, request, obj):
        # Удаляем связанные объекты ManyToMany
        obj.products.all().delete()
        obj.additionals.all().delete()
        obj.services.all().delete()

        # Удаляем менеджера и офис, если они не используются в других заказах
        if not Order.objects.filter(manager=obj.manager).exists():
            obj.manager.delete()

        if not Order.objects.filter(office=obj.office).exists():
            obj.office.delete()
        # Удаляем сам объект
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            # Удаляем связанные объекты ManyToMany
            obj.products.all().delete()
            obj.additionals.all().delete()
            obj.services.all().delete()

            # Удаляем менеджера и офис, если они не используются в других заказах
            if not Order.objects.filter(manager=obj.manager).exclude(pk=obj.pk).exists():
                obj.manager.delete()

            if not Order.objects.filter(office=obj.office).exclude(pk=obj.pk).exists():
                obj.office.delete()

        # Удаляем выбранные объекты
        super().delete_queryset(request, queryset)

class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('system', 'series', 'width', 'height', 'base_color')
    search_fields = ('system', 'series', 'width', 'height', 'base_color')

class AdditionalAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'cost')
    search_fields = ('name', 'quantity', 'cost')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    search_fields = ('name', 'cost')

@admin.register(LogFile)
class LogFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'created_at', 'file_exists', 'download_link', 'delete_button')
    search_fields = ('file_name',)
    readonly_fields = ('file_exists', 'file_size')
    fields = ('file_name', 'created_at', 'file_exists', 'file_size')

    def file_exists(self, obj):
        """Проверяет существование файла на диске"""
        if obj and os.path.exists(obj.file_path()):
            return format_html('<span style="color: green;">✓ Файл существует</span>')
        return format_html('<span style="color: red;">✗ Файл не существует</span>')
    
    def file_size(self, obj):
        """Возвращает размер файла, если он существует"""
        if obj and os.path.exists(obj.file_path()):
            size_bytes = os.path.getsize(obj.file_path())
            if size_bytes < 1024:
                return f"{size_bytes} байт"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes/1024:.2f} КБ"
            else:
                return f"{size_bytes/(1024*1024):.2f} МБ"
        return "—"

    def download_link(self, obj):
        # Добавляем слеш в конец URL, чтобы соответствовать настройке URL в urls.py
        url = reverse('download_log', args=[obj.file_name])
        if not url.endswith('/'):
            url += '/'
        
        if obj and os.path.exists(obj.file_path()):
            return format_html('<a href="{}" target="_blank">Скачать</a>', url)
        return format_html('<span style="color: gray;">Скачать</span>')

    def delete_button(self, obj):
        return format_html('<a href="{}" style="color:red;">Удалить</a>', reverse('delete_log', args=[obj.pk]))

    file_exists.short_description = "Статус файла"
    file_size.short_description = "Размер файла"
    download_link.short_description = "Скачать"
    delete_button.short_description = "Удалить"
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Добавление лог-файла'
        extra_context['additional_info'] = 'При создании записи пустой файл будет создан автоматически.'
        return super().add_view(request, form_url, extra_context)

@admin.register(RawJSON)
class RawJSONAdmin(admin.ModelAdmin):
    list_display = ('order', 'created_at')
    search_fields = ('order__number',)
    readonly_fields = ('data', 'created_at')

@admin.register(ScriptCode)
class ScriptCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'placement', 'is_active')
    list_filter = ('placement', 'is_active')
    search_fields = ('name', 'code')

@admin.register(WebhookSettings)
class WebhookSettingsAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_active', 'description')
    list_filter = ('is_active',)

@admin.register(TemplateSettings)
class TemplateSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)

@admin.register(LogSettings)
class LogSettingsAdmin(admin.ModelAdmin):
    list_display = ('retention_days',)

@admin.register(LogKeyword)
class LogKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'usage_count', 'description')
    search_fields = ('keyword', 'description')
    ordering = ('-usage_count', 'keyword')
    readonly_fields = ('usage_count',)

@admin.register(LogFilter)
class LogFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'log_level', 'get_keywords', 'is_active', 'created_at', 'export_button')
    list_filter = ('log_level', 'is_active', 'keywords')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    filter_horizontal = ('keywords',)
    
    def get_keywords(self, obj):
        """Возвращает список ключевых слов фильтра"""
        if not obj.keywords.exists():
            return '-'
        return ", ".join([kw.keyword for kw in obj.keywords.all()[:5]]) + (
            "..." if obj.keywords.count() > 5 else "")
    
    def export_button(self, obj):
        """Кнопка для экспорта отфильтрованных логов"""
        if obj and obj.is_active:
            url = reverse('export_filtered_log', args=[obj.id])
            return format_html('<a href="{}" target="_blank" class="button">Экспортировать логи</a>', url)
        return '-'
    
    def save_related(self, request, form, formsets, change):
        """Обновляет счетчик использования ключевых слов при сохранении фильтра"""
        super().save_related(request, form, formsets, change)
        # Обновляем счетчики использования ключевых слов
        for keyword in form.instance.keywords.all():
            keyword.usage_count = keyword.filters.count()
            keyword.save()
    
    get_keywords.short_description = "Ключевые слова"
    export_button.short_description = "Экспорт"

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderRating)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Option)
admin.site.register(Product, ProductAdmin)
admin.site.register(Additional, AdditionalAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ChatCode)
admin.site.register(AnalyticsCode)

