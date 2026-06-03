from django.http import JsonResponse, HttpResponse
from django.db import connections
from django.db.utils import OperationalError
from django.views.decorators.http import require_GET


def health(request):
	"""Health check endpoint. Returns service and DB status."""
	db_conn = connections['default']
	try:
		c = db_conn.cursor()
		c.execute('SELECT 1')
		db_ok = True
	except OperationalError:
		db_ok = False

	status = 'ok' if db_ok else 'error'
	return JsonResponse({'status': status, 'database': 'ok' if db_ok else 'down'})


def _get_sensor_by_api_key(key: str):
	from portal.apps.devices.models import Sensor

	if not key:
		return None
	try:
		return Sensor.objects.get(api_key=key)
	except Sensor.DoesNotExist:
		return None


@require_GET
def whoami(request):
	"""Test endpoint to identify the sensor by X-API-Key header."""
	key = request.headers.get('X-API-Key') or request.GET.get('api_key')
	sensor = _get_sensor_by_api_key(key)
	if not sensor:
		return HttpResponse('Unauthorized', status=401)
	return JsonResponse({'identifier': sensor.identifier, 'name': sensor.name, 'sensor_type': sensor.sensor_type.name})
