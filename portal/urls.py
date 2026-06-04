"""
URL configuration for portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('portal.apps.dashboard.urls')),
    # Qualquer acesso à raiz (vazia) será jogado automaticamente para o dashboard
    path('', lambda request: redirect('dashboard:index')), 
]