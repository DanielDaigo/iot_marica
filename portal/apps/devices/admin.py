from django.contrib import admin
from .models import SensorType, Sensor
from django.utils.html import format_html


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
	readonly_fields = ('api_key', 'created_at', 'last_seen')
	search_fields = ('identifier', 'name')
	list_filter = ('sensor_type', 'is_active')
	actions = (rotate_api_key,)
	actions = (rotate_api_key, revoke_api_key)

	def grafana_link(self, obj):
		url = obj.grafana_link()
		if not url:
			return '-'
		return format_html('<a href="{}" target="_blank">Grafana</a>', url)

	grafana_link.short_description = 'Grafana'
