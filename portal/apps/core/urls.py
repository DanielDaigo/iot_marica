from django.urls import path
from .views import health, whoami

urlpatterns = [
    path('health/', health, name='health'),
    path('api/whoami/', whoami, name='whoami'),
]
