from django.conf import settings
from django.http import JsonResponse

def api_key_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        print(request.headers)
        api_key = request.headers.get('APIKEY')

        # Проверка на наличие ключа
        if not api_key:
            return JsonResponse({'error': 'API key not found'}, status=400)

        # Проверка на корректность ключа
        if api_key != settings.API_KEY:
            return JsonResponse({'error': 'Invalid API key'}, status=403)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
