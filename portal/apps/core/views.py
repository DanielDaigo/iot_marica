from django.http import JsonResponse, HttpResponse
from django.db import connections
from django.db.utils import OperationalError
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
@require_POST
def rotate_sensor_key(request, pk: int):
	from portal.apps.devices.models import Sensor

	try:
		sensor = Sensor.objects.get(pk=pk)
	except Sensor.DoesNotExist:
		return JsonResponse({'error': 'not found'}, status=404)

	sensor.rotate_api_key(performed_by=request.user)
	return JsonResponse({'result': 'rotated', 'new_key': sensor.api_key})


@staff_member_required
@require_POST
def revoke_sensor_key(request, pk: int):
	from portal.apps.devices.models import Sensor

	try:
		sensor = Sensor.objects.get(pk=pk)
	except Sensor.DoesNotExist:
		return JsonResponse({'error': 'not found'}, status=404)

	sensor.revoke_api_key(performed_by=request.user)
	return JsonResponse({'result': 'revoked', 'is_active': sensor.is_active})


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
