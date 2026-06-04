from django.contrib import admin
from django.utils.html import format_html
from .models import SensorType, Sensor, SensorApiKeyAudit


@admin.register(SensorApiKeyAudit)
class SensorApiKeyAuditAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'action', 'performed_by', 'created_at')
    readonly_fields = ('sensor', 'action', 'old_key', 'new_key', 'performed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('sensor__name', 'sensor__identifier')


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)


@admin.action(description='Rotate API key for selected sensors')
def rotate_api_key(modeladmin, request, queryset):
    for obj in queryset:
        obj.rotate_api_key(performed_by=request.user)


@admin.action(description='Revoke API key for selected sensors')
def revoke_api_key(modeladmin, request, queryset):
    for obj in queryset:
        obj.revoke_api_key(performed_by=request.user)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name', 'sensor_type', 'is_active', 'last_seen', 'grafana_link')
    
    # Injetamos o grafico_embutido como campo de leitura
    readonly_fields = ('api_key', 'created_at', 'last_seen', 'grafico_embutido')
    search_fields = ('identifier', 'name')
    list_filter = ('sensor_type', 'is_active')
    actions = (rotate_api_key, revoke_api_key)

    # Organização visual da página do sensor no Jazzmin
    fieldsets = (
        ("Identificação e Status", {
            "fields": ("identifier", "name", "sensor_type", "is_active", "last_seen", "created_at")
        }),
        ("Autenticação", {
            "fields": ("api_key",),
            "description": "Selecione o sensor na lista e use a caixa de ações para rotacionar ou revogar a chave."
        }),
        ("Painel de Telemetria (VM 1)", {
            "fields": ("grafico_embutido",),
            "description": "Gráfico gerado dinamicamente pelo Grafana em modo Kiosk."
        }),
    )

    def grafana_link(self, obj):
        url = obj.grafana_link()
        if not url:
            return '-'
        return format_html('<a href="{}" target="_blank">Abrir Externo</a>', url)
    grafana_link.short_description = 'Grafana'

    # Função que renderiza o Iframe na tela de detalhes
    @admin.display(description="Gráfico em Tempo Real")
    def grafico_embutido(self, obj):
        url = obj.grafana_link()
        if not url:
            return "Dashboard não configurado."
        return format_html(
            '<iframe src="{}" width="100%" height="500" frameborder="0" style="border:1px solid #ddd; border-radius:8px;"></iframe>',
            url
        )