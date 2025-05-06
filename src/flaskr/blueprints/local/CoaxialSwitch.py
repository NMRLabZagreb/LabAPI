#!/usr/bin/env python

"""

This file defines a class for communicating with a local Teledyne Coaxial Switch. The class a holds ParallelPort as an attribute and links API calls to device module functions.
set_routes() class method returns a Flask blueprint.

"""

__author__ = "Ivan Jakovac"
__email__ = "ivan.jakovac2@gmail.com"
__version__ = "v0.1"

#  Copyright (C) 2020-2025 Ivan Jakovac
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

from flask import Blueprint, request, jsonify
from ...config import API_KEY
from hashlib import sha256
from ...modules.pyCoaxialSwitch import CoaxialSwitch

# Blueprint is a global variable
blueprint = Blueprint('CoaxialSwitch', __name__, url_prefix='/coaxial_switch')

class localCoaxialSwitch():
    def __init__(self, device_present: bool = True):
        # Instantiate a ParallelPort resource
        self.switch = CoaxialSwitch()

    # Authorization check
    @blueprint.before_request
    def check_api_key():
        if ('x-api-key' not in request.headers.keys(lower=True)) or (sha256(request.headers.get('X-API-Key').encode()).hexdigest() != API_KEY):
            return jsonify({'error': 'Unauthorized'}), 401  
    
    def set_routes(self):
        '''
            A function to set API routes: in most cases API endpoint path == Lakeshore336 class method.
            Most functions are boilerplate and can handle GET and POST methods.
        '''
        @blueprint.route('/get_switch', methods=['GET', 'POST'])
        def get_switch():
            response = self.switch.get_switch()
            if request.method == 'POST':
                return jsonify({'value': response}), 200
            elif request.method == 'GET':
                return str(response), 200
            
        @blueprint.route('/set_switch', methods=['GET', 'PUT', 'POST'])
        def set_switch():
            if request.method == 'POST':
                self.switch.set_switch(str(request.json['to']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.switch.set_switch(str(request.args['to']))
                return str(""), 200

        # Return blueprint to register in Flask app
        return blueprint
