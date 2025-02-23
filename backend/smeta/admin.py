from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Office, Manager, Option, Product, Additional, Service, Order, OrderRating, LogFile, ChatCode, AnalyticsCode


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
    list_display = ('file_name', 'created_at', 'download_link', 'delete_button')

    def download_link(self, obj):
        return format_html('<a href="{}" target="_blank">Скачать</a>', reverse('download_log', args=[obj.file_name]))

    def delete_button(self, obj):
        return format_html('<a href="{}" style="color:red;">Удалить</a>', reverse('delete_log', args=[obj.pk]))

    download_link.short_description = "Скачать"
    delete_button.short_description = "Удалить"

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

