from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from influxdb import InfluxDBClient

from portal.apps.devices.models import Sensor

def get_influx_client():
    return InfluxDBClient(
        host=settings.INFLUXDB_HOST,
        port=settings.INFLUXDB_PORT,
        database=settings.INFLUXDB_DATABASE,
    )

@login_required
def dashboard(request):
    sensors = Sensor.objects.filter(is_active=True).order_by("name")
    device_id = request.GET.get("sensor", sensors.first().identifier if sensors.exists() else None)
    period = request.GET.get("period", "24h")

    period_map = {"24h": "24h", "7d": "7d", "30d": "30d"}
    influx_period = period_map.get(period, "24h")

    labels, temperatures, humidities = [], [], []
    last_temp = last_humidity = record_count = None

    if device_id:
        client = get_influx_client()

        # Série temporal
        query = (
            f"SELECT mean(valor) AS temperatura, mean(umidade) AS umidade "
            f"FROM telemetria_ambiental "
            f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period} "
            f"GROUP BY time(5m) fill(previous)"
        )
        try:
            result = client.query(query)
            points = list(result.get_points())

            for p in points:
                if p.get("temperatura") is not None:
                    labels.append(p["time"])
                    temperatures.append(round(p["temperatura"], 1))
                    humidities.append(round(p["umidade"], 1) if p.get("umidade") else None)

            # Última leitura
            last_query = (
                f"SELECT last(valor) AS temperatura, last(umidade) AS umidade "
                f"FROM telemetria_ambiental WHERE dispositivo = '{device_id}'"
            )
            last_result = list(client.query(last_query).get_points())
            if last_result:
                last_temp = round(last_result[0].get("temperatura", 0), 1)
                last_humidity = last_result[0].get("umidade")
                if last_humidity is not None:
                    last_humidity = round(last_humidity, 1)

            # Contagem de registros
            count_query = (
                f"SELECT count(valor) FROM telemetria_ambiental "
                f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period}"
            )
            count_result = list(client.query(count_query).get_points())
            if count_result:
                record_count = count_result[0].get("count", 0)
        except Exception as e:
            print(f"Erro no InfluxDB: {e}")

    selected_sensor = sensors.filter(identifier=device_id).first()

    return render(request, "dashboard/index.html", {
        "sensors": sensors,
        "selected_sensor": selected_sensor,
        "device_id": device_id,
        "period": period,
        "labels": labels,
        "temperatures": temperatures,
        "humidities": humidities,
        "last_temp": last_temp,
        "last_humidity": last_humidity,
        "record_count": record_count,
    })