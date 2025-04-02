#!/usr/bin/env python

"""

This file is used to create Flask app and register blueprints

"""

__author__ = "Ivan Jakovac"
__email__ = "ivan.jakovac2@gmail.com"
__version__ = "v0.1"

#  Copyright (C) 2020-2024 Ivan Jakovac
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with this program. If not,
#  see <https://www.gnu.org/licenses/>.

from flask import Flask, redirect
from .config import API_KEY, THIS_PC, AVAILABLE_DEVICES
from importlib import import_module

def create_app():
    """
        Instantiate Flask app and register blueprints
    """
    # Create a Flask app 
    app = Flask(__name__)
    app.secret_key = API_KEY
    
    # Route homepage to Swagger frontend
    @app.route('/')
    def homepage():
        return redirect('/swagger/')

    # Register Swagger blueprint
    from .blueprints.swagger import swagger_blueprint
    app.register_blueprint(swagger_blueprint())

    # Dictionary which holds local devices:
    app.local_devices = dict()

    for device, properties in AVAILABLE_DEVICES.items():
        if properties['host'] in ['localhost', '127.0.0.1'] or f"{properties['host']}:{properties['port']}" == THIS_PC:
            # If HOST is local, use local modules connect API calls to respective functions which handle VISA communication
            # Import local device modules
            device_module = import_module(f'.modules.py{device}', package = __package__)
            blueprint_module = import_module(f'.blueprints.local.{device}', package = __package__)
            # Instantiate device: if in debug mode - device will use mock VISA
            app.local_devices[device] = getattr(device_module, f'{device}')(device_present = properties['device_present'])
            local_device_blueprint = getattr(blueprint_module, f'local{device}')(app.local_devices[device])
            app.register_blueprint(local_device_blueprint.set_routes())
        else:
            # If HOST is remote server, use remote modules forward API calls to respective IPs
            module = import_module('.blueprints.remote.set_routes', package = __package__)
            # Set route(s) for each device; different hosts are handled inside set_routes() function
            device_blueprint = module.set_routes(device, properties)
            app.register_blueprint(device_blueprint)

    return app
