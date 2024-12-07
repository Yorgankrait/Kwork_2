from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from .serializers import OrderSerializer
from .services import transform_keys


class SmetaCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Преобразование ключей
        transformed_data = transform_keys(request.data)
        print(transformed_data)
        serializer = OrderSerializer(data=transformed_data)

        if serializer.is_valid():
            order = serializer.save()  # Сохраняем данные через метод `create` сериализатора
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
