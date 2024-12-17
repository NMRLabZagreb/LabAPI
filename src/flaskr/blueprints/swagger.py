#!/usr/bin/env python

"""

Flask blueprint for a Swagger: define & describe API endpoints by combining .yaml files for all devices listed in AVAILABLE_DEVICES configuration file.

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

from flask_swagger_ui import get_swaggerui_blueprint
from flask import app
from ..config import AVAILABLE_DEVICES
import os

def swagger_blueprint():
    '''
    Flask blueprint constructor function.
    '''
    # Define Swagger path and merged .yaml file location (API endpoint definitions)
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger/swagger.yaml'

    # Call a procedure to merge .yaml files for AVAILABLE_DEVICES
    swagger_constructor()

    # Call a function to construct the blueprint
    swagger_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "LabAPI",
            'tryItOutEnabled': True,
            'docExpansion': 'none',
            'defaultModelsExpandDepth': -1
        },
    )
    # Return the blueprint to register in Flask app
    return swagger_blueprint

def swagger_constructor():
    '''
        Procedure to merge base.yaml with device.yaml file(s) for all devices listed in AVAILABLE_DEVICES
    '''
    # Open and read base.yaml
    with open('flaskr/static/swagger/base.yaml', 'r') as base_file:
        swagger_string = base_file.read()+'\n'

    # Add each device only if device.yaml exists
    for device, properties in AVAILABLE_DEVICES.items():
        if os.path.exists(os.path.abspath(f'flaskr/static/swagger/{device}.yaml')):
            swagger_string += f'tags:\n'
            swagger_string += f'  - name: {properties["name"]}\n'
            swagger_string += f'    description: {properties["description"]}\n'
            swagger_string += f'paths:\n'
            with open(f'flaskr/static/swagger/{device}.yaml') as device_file:
                swagger_string += device_file.read()
    
    # Finally, write merged swagger.yaml to disk
    with open(f'flaskr/static/swagger/swagger.yaml', 'w') as output_file:
        output_file.write(swagger_string)