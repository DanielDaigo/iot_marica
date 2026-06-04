from django.db import models
from django.utils import timezone
from django.conf import settings
import secrets


def _generate_api_key():
    # token_urlsafe gives variable length; limit to 64 chars
    return secrets.token_urlsafe(48)[:64]


class SensorType(models.Model):
    """Defines a type of sensor (e.g., temperature, humidity, battery)."""
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Sensor"
        verbose_name_plural = "Tipos de Sensor"

    def __str__(self):
        return self.name


class SensorApiKeyAudit(models.Model):
    ACTION_CHOICES = [
        ('rotate', 'Rotate'),
        ('revoke', 'Revoke'),
        ('set', 'Set'),
    ]

    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='api_key_audits')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    old_key = models.CharField(max_length=128, blank=True, null=True)
    new_key = models.CharField(max_length=128, blank=True, null=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sensor API Key Audit'
        verbose_name_plural = 'Sensor API Key Audits'

    def __str__(self):
        return f"{self.sensor.identifier} - {self.action} @ {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class Sensor(models.Model):
    """Represents an inventory entry for a physical sensor attached to a node/device."""
    identifier = models.CharField(max_length=100, unique=True, help_text="Identificador único do sensor (ex: mac, serial, node+index)")
    name = models.CharField(max_length=150)
    sensor_type = models.ForeignKey(SensorType, on_delete=models.PROTECT, related_name='sensors')
    location = models.CharField(max_length=200, blank=True, null=True)
    hardware = models.CharField(max_length=200, blank=True, null=True, help_text="Informação de hardware / modelo")
    is_active = models.BooleanField(default=True)
    api_key = models.CharField(max_length=64, unique=True, default=_generate_api_key)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensores"

    def __str__(self):
        return f"{self.name} ({self.identifier})"

    def rotate_api_key(self, performed_by=None):
        """Rotate the API key and record an audit entry."""
        old = self.api_key
        self.api_key = _generate_api_key()
        self.save(update_fields=['api_key'])
        try:
            SensorApiKeyAudit.objects.create(sensor=self, action='rotate', old_key=old, new_key=self.api_key, performed_by=getattr(performed_by, 'pk', None) and performed_by)
        except Exception:
            # Do not fail on audit errors
            pass

    def revoke_api_key(self, performed_by=None):
        """Revoke the API key by rotating and disabling the sensor."""
        old = self.api_key
        self.api_key = _generate_api_key()
        self.is_active = False
        self.save(update_fields=['api_key', 'is_active'])
        try:
            SensorApiKeyAudit.objects.create(sensor=self, action='revoke', old_key=old, new_key=self.api_key, performed_by=getattr(performed_by, 'pk', None) and performed_by)
        except Exception:
            pass

    def mark_seen(self):
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])

    def grafana_link(self, panel_params: dict | None = None, base_url: str | None = None) -> str:
        """Build a Grafana URL for this sensor using optional parameters.

        - `panel_params` will be appended as query params.
        - If `base_url` is not provided, attempts to read `GRAFANA_BASE_URL` from settings.
        """
        from urllib.parse import urlencode

        base = base_url or getattr(settings, 'GRAFANA_BASE_URL', '')
        if not base:
            return ''

        params = panel_params.copy() if panel_params else {}
        # Include sensor identifier so Grafana dashboard can filter to this sensor
        params.setdefault('var-sensor', self.identifier)
        q = urlencode(params)
        return f"{base.rstrip('/')}/?{q}"