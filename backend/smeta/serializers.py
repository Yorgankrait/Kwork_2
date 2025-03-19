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
            'options', 'quantity', 'image', 'cost'
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
        """
        with transaction.atomic():
            # Извлекаем данные для связанных объектов
            office_data = validated_data.pop('office')
            manager_data = validated_data.pop('manager')
            products_data = validated_data.pop('products')
            additionals_data = validated_data.pop('additionals', [])
            services_data = validated_data.pop('services', [])

            # Создаем основные объекты
            office = self._create_office(office_data)
            manager = self._create_manager(manager_data)
            order = self._create_order(office, manager, validated_data)

            # Добавляем связанные объекты
            self._add_products_to_order(order, products_data)
            self._add_additionals_to_order(order, additionals_data)
            self._add_services_to_order(order, services_data)

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
        options_list = []

        for product_data in products_data:

            options_data = product_data.pop('options', [])
            options_list.append(options_data)
            product = Product.objects.create(**product_data)
            products.append(product)


        for product, options_data in zip(products, options_list):
            options = []
            for option_data in options_data:
                option = Option.objects.create(**option_data)
                options.append(option)

            if options:
                product.options.set(options)
            order.products.add(product)

    def _add_additionals_to_order(self, order, additionals_data):
        additionals = []
        for additional_data in additionals_data:
            additional = Additional.objects.create(**additional_data)
            additionals.append(additional)

        for additional in additionals:
            order.additionals.add(additional)

    def _add_services_to_order(self, order, services_data):
        services = []
        for service_data in services_data:
            service = Service.objects.create(**service_data)
            services.append(service)

        for service in services:
            order.services.add(service)