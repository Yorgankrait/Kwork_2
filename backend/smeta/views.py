import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OrderSerializer
from .services import transform_keys, get_or_create_user_id
from .tasks import generate_pdf_task
from .models import Order, OrderRating


class SmetaCreateAPIView(APIView):
    """ Сохраняет смету разбивая на объекты """
    def post(self, request, *args, **kwargs):
        # Преобразование ключей
        transformed_data = transform_keys(request.data)
        serializer = OrderSerializer(data=transformed_data)

        if serializer.is_valid():
            order = serializer.save()  # Сохраняем данные через метод `create` сериализатора
            generate_pdf_task.delay(order.id) # Генерируем PDF файл на базе сметы и сохраняем
            return Response(f'Смета номер: {order.number} успешно создана', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def smeta_details(request, number):
    """ Возвращает страницу сметы по её номеру и автоматически генерирует PDF """
    order = get_object_or_404(Order, number=number)

    user_id = get_or_create_user_id(request)
    user_rating = OrderRating.objects.filter(order=order, user_id=user_id).first()

    total_additionals_cost = sum([additional.cost for additional in order.additionals.all()])
    total_services_cost = sum([service.cost for service in order.services.all()])

    context = {
        'order': order,
        'office': order.office,
        'manager': order.manager,
        'products': order.products.all(),
        'additionals': order.additionals.all(),
        'services': order.services.all(),
        'total_additionals_cost': total_additionals_cost,
        'total_services_cost': total_services_cost,
        'user_rating': user_rating
    }

    return render(request, 'order_detail.html', context)


def rate_smeta(request, number):
    """Обрабатывает оценку заказа"""
    order = get_object_or_404(Order, number=number)

    if request.method == 'POST':
        # Декодируем JSON из тела запроса
        try:
            data = json.loads(request.body)
            liked = data.get('liked')
            print(liked)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # Получаем user_id из cookies или генерируем новый
        user_id = get_or_create_user_id(request)

        # Обновляем или создаем запись об оценке
        rating, created = OrderRating.objects.update_or_create(
            order=order,
            user_id=user_id,
            defaults={'liked': liked},
        )

        response = JsonResponse({'success': True, 'liked': rating.liked, 'created': created})

        # Устанавливаем user_id в cookies, если его не было
        if not request.COOKIES.get('user_id'):
            response.set_cookie('user_id', user_id, max_age=365 * 24 * 60 * 60)  # Срок действия 1 год

        return response
