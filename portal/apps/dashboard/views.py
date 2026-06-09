from django.shortcuts import render
from django.conf import settings
from influxdb import InfluxDBClient
import json

from portal.apps.devices.models import Sensor

def get_influx_client():
    return InfluxDBClient(
        host=settings.INFLUXDB_HOST,
        port=settings.INFLUXDB_PORT,
        username=settings.INFLUXDB_USER,
        password=settings.INFLUXDB_PASSWORD,
        database=settings.INFLUXDB_DATABASE,
    )

def dashboard(request):
    sensors = Sensor.objects.filter(is_active=True).order_by("name")
    device_id = request.GET.get("sensor", sensors.first().identifier if sensors.exists() else None)
    period = request.GET.get("period", "15m")

    # Mapeamento de tempo e agrupamento
    period_map = {
        "15m": ("15m", "5s"),
        "1h": ("1h", "1m"),
        "6h": ("6h", "5m"),
        "24h": ("24h", "15m"),
        "7d": ("7d", "1h"),
        "30d": ("30d", "6h"),
    }
    influx_period, group_time = period_map.get(period, ("15m", "5s"))

    labels, temperatures, humidities = [], [], []
    last_temp = last_humidity = record_count = None
    temp_min = temp_max = hum_min = hum_max = None
    temp_trend = hum_trend = "estável"

    if device_id:
        client = get_influx_client()

        # Query principal
        query = (
            f"SELECT mean(valor) AS temperatura, mean(umidade) AS umidade "
            f"FROM telemetria_ambiental "
            f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period} "
            f"GROUP BY time({group_time}) fill(null)"
        )
        try:
            result = client.query(query)
            points = list(result.get_points())

            for p in points:
                if p.get("temperatura") is not None or p.get("umidade") is not None:
                    labels.append(p["time"])
                    temperatures.append(round(p["temperatura"], 1) if p.get("temperatura") is not None else None)
                    humidities.append(round(p["umidade"], 1) if p.get("umidade") is not None else None)

            # Última leitura
            last_query = (
                f"SELECT last(valor) AS temperatura, last(umidade) AS umidade "
                f"FROM telemetria_ambiental "
                f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period}"
            )
            last_result = list(client.query(last_query).get_points())
            if last_result:
                last_temp = round(last_result[0].get("temperatura", 0), 1) if last_result[0].get("temperatura") is not None else None
                last_humidity = round(last_result[0].get("umidade", 0), 1) if last_result[0].get("umidade") is not None else None

            # Contagem de registros
            count_query = (
                f"SELECT count(valor) FROM telemetria_ambiental "
                f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period}"
            )
            count_result = list(client.query(count_query).get_points())
            if count_result:
                record_count = count_result[0].get("count", 0)

            # Mínimos e Máximos
            minmax_query = (
                f"SELECT min(valor) AS temp_min, max(valor) AS temp_max, "
                f"min(umidade) AS hum_min, max(umidade) AS hum_max "
                f"FROM telemetria_ambiental "
                f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period}"
            )
            minmax_result = list(client.query(minmax_query).get_points())
            if minmax_result:
                temp_min = round(minmax_result[0].get("temp_min", 0), 1) if minmax_result[0].get("temp_min") is not None else None
                temp_max = round(minmax_result[0].get("temp_max", 0), 1) if minmax_result[0].get("temp_max") is not None else None
                hum_min  = round(minmax_result[0].get("hum_min", 0), 1) if minmax_result[0].get("hum_min") is not None else None
                hum_max  = round(minmax_result[0].get("hum_max", 0), 1) if minmax_result[0].get("hum_max") is not None else None

            # Cálculo de Tendência
            valid_temps = [t for t in temperatures if t is not None]
            valid_humids = [h for h in humidities if h is not None]
            if len(valid_temps) >= 2:
                diff = valid_temps[-1] - valid_temps[0]
                temp_trend = "subindo" if diff > 0.3 else "caindo" if diff < -0.3 else "estável"
            if len(valid_humids) >= 2:
                diff = valid_humids[-1] - valid_humids[0]
                hum_trend = "subindo" if diff > 1 else "caindo" if diff < -1 else "estável"

        except Exception as e:
            print(f"Erro no InfluxDB: {e}")

    selected_sensor = sensors.filter(identifier=device_id).first()

    context = {
        "sensors": sensors,
        "selected_sensor": selected_sensor,
        "device_id": device_id,
        "period": period,
        "labels": json.dumps(labels),
        "temperatures": json.dumps(temperatures),
        "humidities": json.dumps(humidities),
        "last_temp": last_temp,
        "last_humidity": last_humidity,
        "last_temp_json": json.dumps(last_temp),
        "last_humidity_json": json.dumps(last_humidity),
        "record_count": record_count,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "hum_min": hum_min,
        "hum_max": hum_max,
        "temp_trend": temp_trend,
        "hum_trend": hum_trend,
        "has_temp_data": any(t is not None for t in temperatures),
        "has_hum_data": any(h is not None for h in humidities),
    }

    if request.GET.get('fetch') == 'true':
        from django.http import JsonResponse
        return JsonResponse({
            "labels": labels,
            "temperatures": temperatures,
            "humidities": humidities,
            "last_temp": last_temp,
            "last_humidity": last_humidity,
            "record_count": record_count,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "hum_min": hum_min,
            "hum_max": hum_max,
            "temp_trend": temp_trend,
            "hum_trend": hum_trend,
            "has_temp_data": any(t is not None for t in temperatures),
            "has_hum_data": any(h is not None for h in humidities),
        })

    return render(request, "dashboard/index.html", context)