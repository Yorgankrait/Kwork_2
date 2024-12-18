from django.db import transaction
from rest_framework.serializers import ModelSerializer
from .models import Office, Manager, Option, Product, Additional, Service, Order


class OfficeSerializer(ModelSerializer):
    class Meta:
        model = Office
        fields = ['name', 'address']

class ManagerSerializer(ModelSerializer):
    class Meta:
        model = Manager
        fields = ['name', 'phone']

class OptionSerializer(ModelSerializer):
    class Meta:
        model = Option
        fields = ['name']

class ProductSerializer(ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'identifier', 'system', 'series', 'width', 'height',
            'base_color', 'inner_color', 'outer_color', 'handles',
            'options', 'quantity', 'image'
        ]

class AdditionalSerializer(ModelSerializer):
    class Meta:
        model = Additional
        fields = ['name', 'quantity', 'cost']

class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'cost']

class OrderSerializer(ModelSerializer):
    office = OfficeSerializer()
    manager = ManagerSerializer()
    products = ProductSerializer(many=True)
    additionals = AdditionalSerializer(many=True, required=False, allow_empty=True)
    services = ServiceSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = Order
        fields = [
            'number', 'office', 'manager',
            'old_price', 'new_price', 'products',
            'additionals', 'services'
        ]

    def create(self, validated_data):
        """
        Создание нового заказа с вложенными объектами: office, manager, products, additionals, services.
        Используются методы get_or_create для обеспечения уникальности объектов.
        """
        with transaction.atomic():
            # Извлекаем данные для связанных объектов и удаляем их из validated_data
            office_data = validated_data.pop('office')
            manager_data = validated_data.pop('manager')
            products_data = validated_data.pop('products')
            additionals_data = validated_data.pop('additionals', [])
            services_data = validated_data.pop('services', [])

            office = self._create_office(office_data) # Создание объекта Office
            manager = self._create_manager(manager_data) # Создание объекта Manager
            order = self._create_order(office, manager, validated_data) # Создание основного объекта Order

            self._add_products_to_order(order, products_data) # Создание и добавление продуктов к заказу
            self._add_additionals_to_order(order, additionals_data) # Создание и добавление дополнительных услуг к заказу
            self._add_services_to_order(order, services_data) # Создание и добавление сервисов к заказу

            return order


    def _create_office(self, office_data):
        office = Office.objects.create(**office_data)
        return office

    def _create_manager(self, manager_data):
        manager = Manager.objects.create(**manager_data)
        return manager

    def _create_order(self, office, manager, validated_data):
        order = Order.objects.create(office=office, manager=manager, **validated_data)
        return order

    def _add_products_to_order(self, order, products_data):
        products = []
        # Сначала создаем все продукты
        for product_data in products_data:
            options_data = product_data.pop('options')  # Извлекаем опции для продукта
            product = self._create_product(product_data)  # Создаем объект продукта
            products.append(product)  # Добавляем продукт в список

        # Массовое создание продуктов
        Product.objects.bulk_create(products)

        # Теперь устанавливаем связи ManyToMany (опции)
        for product, product_data in zip(products, products_data):
            options_data = product_data.get('options', [])
            self._add_options_to_product(product, options_data)  # Устанавливаем опции для продукта

            # Привязываем продукт к заказу
            order.products.add(product)

    def _create_product(self, product_data):
        return Product(**product_data)

    def _add_options_to_product(self, product, options_data):
        options = []
        for option_data in options_data:
            option = Option.objects.create(**option_data)
            options.append(option)
        product.options.set(options)

    def _add_additionals_to_order(self, order, additionals_data):
        additionals = []
        for additional_data in additionals_data:
            additional = Additional(**additional_data)
            additionals.append(additional)

        Additional.objects.bulk_create(additionals)
        order.additionals.set(additionals)

    def _add_services_to_order(self, order, services_data):
        services = []
        for service_data in services_data:
            service = Service(**service_data)
            services.append(service)

        Service.objects.bulk_create(services)
        order.services.set(services)
