#!/usr/bin/env python

"""

This file defines a class for communicating with a local Keysight E5080A device. The class a holds VISA resource as an attribute and links API calls to device module functions.
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
from ...modules.pyKeysightE5080A import KeysightE5080A

# Blueprint is a global variable
blueprint = Blueprint('KeysightE5080A', __name__, url_prefix='/keysighte5080a')

class localKeysightE5080A():
    def __init__(self, device_present: bool = False):
        # Instantiate a VISA resource; KeysightE5080A class implements various VISA queries as class methods
        self.VNA = KeysightE5080A(device_present=device_present)
        
    # Authorization check
    @blueprint.before_request
    def check_api_key():
        if ('x-api-key' not in request.headers.keys(lower=True)) or (sha256(request.headers.get('X-API-Key').encode()).hexdigest() != API_KEY):
            return jsonify({'error': 'Unauthorized'}), 401
    
    def set_routes(self):
        '''
            A function to set API routes: in most cases API endpoint path == KeysightE5080A class method.
            Most functions are boilerplate and can handle GET and POST methods.
        '''
        @blueprint.route('/get_marker_X', methods=['GET', 'POST'])
        def get_marker_X():
            if request.method == 'POST':
                response_value = self.VNA.get_marker_X(int(request.json['marker_index']))
                return jsonify({'frequency': response_value}), 200
            elif request.method == 'GET':
                response_value = self.VNA.get_marker_X(int(request.args['marker_index']))
                return str(response_value), 200
            
        @blueprint.route('/get_marker_Y', methods=['GET', 'POST'])
        def get_marker_Y():
            if request.method == 'POST':
                response_value = self.VNA.get_marker_Y(int(request.json['marker_index']))
                return jsonify({'amplitude': response_value}), 200
            elif request.method == 'GET':
                response_value = self.VNA.get_marker_Y(int(request.args['marker_index']))
                return str(response_value), 200
            
        @blueprint.route('/get_marker_Y_at', methods=['GET', 'POST'])
        def get_marker_Y_at():
            if request.method == 'POST':
                response_value = self.VNA.get_marker_Y_at(int(request.json['marker_index']),
                                                          float(request.json['frequency']))
                return jsonify({'amplitude': response_value}), 200
            elif request.method == 'GET':
                response_value = self.VNA.get_marker_Y_at(int(request.args['marker_index']),
                                                          float(request.args['frequency']))
                return str(response_value), 200

        @blueprint.route('/get_minimum', methods=['GET', 'POST'])
        def get_minimum():
            if request.method == 'POST':
                response_value = self.VNA.get_minimum(int(request.json['marker_index']))
                return jsonify({'frequency': response_value}), 200
            elif request.method == 'GET':
                response_value = self.VNA.get_minimum(int(request.args['marker_index']))
                return str(response_value), 200

        @blueprint.route('/get_sweep_points', methods=['GET', 'POST'])
        def get_sweep_points():
            response_value = self.VNA.get_sweep_points()
            if request.method == 'POST':
                return jsonify({"points": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
    
        @blueprint.route('/get_Q', methods=['GET', 'POST'])
        def get_Q():
            if request.method == 'POST':
                response_value = self.VNA.get_Q(int(request.json['marker_index']))
                return jsonify({"q": response_value}), 200
            elif request.method == 'GET':
                response_value = self.VNA.get_Q(int(request.args['marker_index']))
                return str(response_value), 200
        
        @blueprint.route('/get_sweep_range', methods=['GET', 'POST'])
        def get_sweep_range():
            response_value = self.VNA.get_sweep_range()
            if request.method == 'POST':
                return jsonify({"start": response_value[0],
                                "stop": response_value[1]}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_filter', methods=['GET', 'POST'])
        def get_filter():
            if request.method == 'POST':
                response_value = self.VNA.get_filter(int(request.json['marker_index']),
                                                     float(request.json['threshold']))
                return jsonify({"bandwidth": response_value[0],
                                "center": response_value[1],
                                "q": response_value[2],
                                "insertion_loss": response_value[3]}), 200
            elif request.method == 'GET':
                response_value = self.VNA.get_filter(int(request.args['marker_index']),
                                                     float(request.args['threshold']))
                return str(response_value), 200
            
        @blueprint.route('/get_complex_data', methods=['GET', 'POST'])
        def get_complex_data():
            response_value = self.VNA.get_complex_data()
            if request.method == 'POST':
                return jsonify({"data": response_value}), 200
            elif request.method == 'GET':
                output_string = '\n'.join([f"{point[0]:.2f}\t{point[1]}" for point in response_value])
                return output_string, 200
        
        @blueprint.route('/set_marker_X', methods=['GET', 'PUT', 'POST'])
        def set_marker_X():
            if request.method == 'POST':
                self.VNA.set_marker_X(int(request.json['marker_index']),float(request.json['frequency']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == "PUT":
                self.VNA.set_marker_X(int(request.args['marker_index']),float(request.args['frequency']))
                return str(""), 200
            
        @blueprint.route('/set_sweep_points', methods=['GET', 'PUT', 'POST'])
        def set_sweep_points():
            if request.method == 'POST':
                self.VNA.set_sweep_points(int(request.json['points']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                print(request.args)
                self.VNA.set_sweep_points(int(request.args['points']))
                return str(""), 200
            
        @blueprint.route('/set_sweep_range', methods=['GET', 'PUT', 'POST'])
        def set_sweep_range():
            if request.method == 'POST':
                self.VNA.set_sweep_range(float(request.json['start']),float(request.json['stop']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.VNA.set_sweep_range(float(request.args['start']),float(request.args['stop']))
                return str(""), 200

        # Return blueprint to register in Flask app
        return blueprint