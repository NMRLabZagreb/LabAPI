#!/usr/bin/env python

"""

This function sets remote routes to comunicate with remote devices. For a given device, function finds its host and forwards API call(s) with all headers and data.

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

from flask import Blueprint, request, jsonify
import requests
from ...config import API_KEY
from hashlib import sha256
        
def set_routes(device, properties):
    """
        Sets routes for remote API calls
    """
    # Instantiate blueprint for a new device - new prefix
    blueprint = Blueprint(device, __name__, url_prefix=f'/{device.lower()}')
    # Construct an URL template knowing the device's host and port
    request_url_template = f'https://{properties["host"]}/{device.lower()}/'

    # Authorization check
    @blueprint.before_request
    def check_api_key():
        if ('x-api-key' not in request.headers.keys(lower=True)) or (sha256(request.headers.get('X-API-Key').encode()).hexdigest() != API_KEY):
            return jsonify({'error': 'Unauthorized'}), 401

    # Catch every call and forward it
    @blueprint.route('/<path:path>', methods=['GET', 'PUT', 'POST'])
    def forward_api_call(path):
        request_url = f'{request_url_template}{path}?{request.query_string.decode()}'
        if request.method == 'GET':
            # For GET call forward full request URL with queries and HTTP headers
            response = requests.get(request_url, headers=request.headers)
            return response.text, response.status_code
        elif request.method == 'PUT':
            # For PUT call forward full request URL with queries and HTTP headers
            response = requests.put(request_url, headers=request.headers)
            return response.text, response.status_code
        elif request.method == 'POST':
            # For POST call forward request URL, HTTP headers and JSON payload
            request_url = request_url_template + path
            response = requests.post(request_url, headers=request.headers, data=request.data)
            return jsonify(response.json()), response.status_code
        
    # Return a blueprint to register in the Flask app        
    return blueprint