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
        
        # Извлекаем данные для связанных объектов и удаляем их из validated_data
        office_data = validated_data.pop('office')
        manager_data = validated_data.pop('manager')
        products_data = validated_data.pop('products')
        additionals_data = validated_data.pop('additionals', [])
        services_data = validated_data.pop('services', [])

        # Создание или извлечение объекта Office
        office = self._get_or_create_office(office_data)

        # Создание или извлечение объекта Manager
        manager = self._get_or_create_manager(manager_data)

        # Создание основного объекта Order
        order = self._get_or_create_order(office, manager, validated_data)

        # Создание и добавление продуктов к заказу
        self._add_products_to_order(order, products_data)

        # Создание и добавление дополнительных услуг к заказу
        self._add_additionals_to_order(order, additionals_data)

        # Создание и добавление сервисов к заказу
        self._add_services_to_order(order, services_data)

        return order


    def _get_or_create_office(self, office_data):
        office, _ = Office.objects.get_or_create(**office_data)
        return office
    
    def _get_or_create_manager(self, manager_data):
        manager, _ = Manager.objects.get_or_create(**manager_data)
        return manager
    
    def _get_or_create_order(self, office, manager, validated_data):
        order, _ = Order.objects.get_or_create(office=office, manager=manager, **validated_data)
        return order
    
    def _add_products_to_order(self, order, products_data):
        for product_data in products_data:
            options_data = product_data.pop('options')  # Извлекаем опции для продукта
            product = self._get_or_create_product(product_data)
    
            # Добавление опций для каждого продукта
            self._add_options_to_product(product, options_data)
    
            # Добавление продукта в заказ
            order.products.add(product)
    
    def _get_or_create_product(self, product_data):
        product, _ = Product.objects.get_or_create(**product_data)
        return product
    
    def _add_options_to_product(self, product, options_data):
        for option_data in options_data:
            option, _ = Option.objects.get_or_create(**option_data)
            product.options.add(option)
    
    def _add_additionals_to_order(self, order, additionals_data):
        for additional_data in additionals_data:
            additional, _ = Additional.objects.get_or_create(**additional_data)
            order.additionals.add(additional)
    
    def _add_services_to_order(self, order, services_data):
        for service_data in services_data:
            service, _ = Service.objects.get_or_create(**service_data)
            order.services.add(service)