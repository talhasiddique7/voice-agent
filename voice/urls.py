from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import views_debug

urlpatterns = [
    path('', views.home, name='home'),
    path('api/process-with-groq/', views.process_with_groq, name='process_with_groq'),
    path('api/upload-audio/', views.upload_audio, name='upload_audio'),
    path('api/debug/env/', views.debug_env, name='debug_env'),
    path('api/debug/groq/', views_debug.check_groq_connection, name='debug_groq'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
