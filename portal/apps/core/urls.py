from django.urls import path
from .views import health, whoami, rotate_sensor_key, revoke_sensor_key

urlpatterns = [
    path('health/', health, name='health'),
    path('api/whoami/', whoami, name='whoami'),
    path('admin/sensors/<int:pk>/rotate/', rotate_sensor_key, name='admin-sensor-rotate'),
    path('admin/sensors/<int:pk>/revoke/', revoke_sensor_key, name='admin-sensor-revoke'),
]
