from waitress import serve
from prometheus_client import start_http_server
from flaskr import create_app

# Create Flask app
app = create_app()

# Serve Prometheus metrics
start_http_server(2025)

# Serve it on localhost:5000
serve(app, host='127.0.0.1', port='5000', threads=1)