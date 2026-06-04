"""
URL configuration for portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('portal.apps.dashboard.urls')),
    
    # Captura APENAS a raiz (/) e joga pro dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    
    # Restaura o core e a API que foram apagados
    path('', include('portal.apps.core.urls')), 
]