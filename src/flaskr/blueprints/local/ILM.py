#!/usr/bin/env python

"""

This file defines a class for communicating with a local ILM device. The class a holds VISA resource as an attribute and links API calls to device module functions.
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
from ...modules.pyILM import ILM

# Blueprint is a global variable
blueprint = Blueprint('ILM', __name__, url_prefix='/ilm')

class localILM():
    def __init__(self, device_present: bool = False):
        # Instantiate a VISA resource; ILM class implements various VISA queries as class methods
        self.ips = ILM(device_present=device_present)
        
    # Authorization check
    @blueprint.before_request
    def check_api_key():
        if ('x-api-key' not in request.headers.keys(lower=True)) or (sha256(request.headers.get('X-API-Key').encode()).hexdigest() != API_KEY):
            return jsonify({'error': 'Unauthorized'}), 401
    
    def set_routes(self):
        '''
            A function to set API routes: in most cases API endpoint path == ILM class method.
            Most functions are boilerplate and can handle GET and POST methods.
        '''
        @blueprint.route('/get_lhe_level', methods=['GET', 'POST'])
        def get_LHe_level():
            response_value = self.ips.get_LHe_level()
            if request.method == 'POST':            
                return jsonify({'LHe_level': response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_ln2_level', methods=['GET', 'POST'])
        def get_LN2_level():
            response_value = self.ips.get_LN2_level()
            if request.method == 'POST':
                return jsonify({'LN2_level': response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200         

        # Return blueprint to register in Flask app
        return blueprint
