from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from unfold.decorators import action, display

from .models import SensorType, Sensor, SensorApiKeyAudit


@admin.register(SensorApiKeyAudit)
class SensorApiKeyAuditAdmin(ModelAdmin): 
    list_display = ('sensor', 'action', 'performed_by', 'created_at')
    readonly_fields = ('sensor', 'action', 'old_key', 'new_key', 'performed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('sensor__name', 'sensor__identifier')

    # Travas de Imutabilidade
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SensorType)
class SensorTypeAdmin(ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)


@admin.action(description='Girar chaves em massa')
def rotate_api_key(modeladmin, request, queryset):
    for obj in queryset:
        obj.rotate_api_key(performed_by=request.user)

@admin.action(description='Revogar chaves em massa')
def revoke_api_key(modeladmin, request, queryset):
    for obj in queryset:
        obj.revoke_api_key(performed_by=request.user)


@admin.register(Sensor)
class SensorAdmin(ModelAdmin):
    list_display = ('identifier', 'name', 'sensor_type', 'get_is_active', 'last_seen', 'grafana_link')
    readonly_fields = ('api_key', 'created_at', 'last_seen')
    search_fields = ('identifier', 'name')
    list_filter = ('sensor_type', 'is_active')
    actions = (rotate_api_key, revoke_api_key)
    
    fieldsets = (
        ("Identificação", {
            "fields": ("identifier", "name", "sensor_type", "is_active")
        }),
        ("Hardware e Local", {
            "fields": ("hardware", "location", "last_seen"),
        }),
        ("Segurança e API", {
            "fields": ("api_key", "created_at"),
            "description": "Utilize os botões no topo para girar ou revogar a chave de API."
        }),
    )

    @display(description="Ativo", boolean=True, label=True)
    def get_is_active(self, obj):
        return obj.is_active

    @display(description='Grafana')
    def grafana_link(self, obj):
        url = obj.grafana_link()
        if not url:
            return '-'
        return format_html('<a href="{}" target="_blank">Abrir Externo</a>', url)