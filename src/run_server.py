from waitress import serve
from flaskr import create_app

# Create Flask app
app = create_app()

# Serve it on localhost:5000
serve(app, host='127.0.0.1', port='5000', threads=1)