from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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

@login_required
def dashboard(request):
    sensors = Sensor.objects.filter(is_active=True).order_by("name")
    device_id = request.GET.get("sensor", sensors.first().identifier if sensors.exists() else None)
    period = request.GET.get("period", "15m") # Default mais granular para testes rápidos

    # Mapeamento granular: (Tempo de busca, Agrupamento de resolução)
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

    if device_id:
        client = get_influx_client()

        # fill(null) evita desenhar gráficos com dados de testes passados
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

            # Limitamos a última leitura ao período selecionado para matar fantasmas antigos
            last_query = (
                f"SELECT last(valor) AS temperatura, last(umidade) AS umidade "
                f"FROM telemetria_ambiental "
                f"WHERE dispositivo = '{device_id}' AND time > now() - {influx_period}"
            )
            last_result = list(client.query(last_query).get_points())
            if last_result:
                last_temp = round(last_result[0].get("temperatura", 0), 1) if last_result[0].get("temperatura") is not None else None
                last_humidity = round(last_result[0].get("umidade", 0), 1) if last_result[0].get("umidade") is not None else None

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
        "labels": json.dumps(labels),
        "temperatures": json.dumps(temperatures),
        "humidities": json.dumps(humidities),
        "last_temp": last_temp,
        "last_humidity": last_humidity,
        "record_count": record_count,
    })