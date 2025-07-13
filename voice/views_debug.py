import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def check_groq_connection(request):
    """Debug endpoint to check GROQ connection and environment"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    return JsonResponse({
        'success': bool(groq_api_key),
        'groq_api_key_loaded': bool(groq_api_key),
        'groq_api_key_length': len(groq_api_key) if groq_api_key else 0,
        'python_path': os.getenv("PYTHONPATH"),
        'django_settings_module': os.getenv("DJANGO_SETTINGS_MODULE"),
        'environment': dict(os.environ).get('ENVIRONMENT', 'development'),
    })
