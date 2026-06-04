"""
URL configuration for portal project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('portal.apps.dashboard.urls')),  # <-- Rota exclusiva do novo painel
    path('', include('portal.apps.core.urls')),                 # <-- Mantém o seu app core intacto na raiz
]