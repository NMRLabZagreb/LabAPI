from waitress import serve

from prometheus_client import start_http_server
from prometheusWorker import PrometheusWorker
from flaskr import create_app
from threading import Thread

# Create Flask app
app = create_app()

# Instantiate threaded Prometheus Worker which periodically updates Prometheus metrics
prometheus_updater = PrometheusWorker(app)
theaded_client = Thread(target = prometheus_updater.run)
theaded_client.daemon = True
theaded_client.start()

# Serve Prometheus metrics
start_http_server(2025)

# Serve it on localhost:5000
serve(app, host='127.0.0.1', port='5000', threads=1)