#!/usr/bin/env python

"""

This file defines a class for communicating with a local Lakeshore 336 device. The class a holds VISA resource as an attribute and links API calls to device module functions.
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
from prometheus_client import Gauge, Enum
from ...config import API_KEY
from hashlib import sha256
from ...modules.pyLakeshore336 import Lakeshore336

# Blueprint is a global variable
blueprint = Blueprint('Lakeshore336', __name__, url_prefix='/lakeshore336')

class localLakeshore336():
    def __init__(self, device_present: bool = False):
        # Instantiate a VISA resource; KeysightE5080A class implements various VISA queries as class methods
        self.ls = Lakeshore336(device_present=device_present)

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
        @blueprint.route('/get_temperature', methods=['GET', 'POST'])
        def get_temperature():
            if request.method == 'POST':
                response_value = self.ls.get_temperature(str(request.json['control_channel']))
                return jsonify({'temperature': response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_temperature(str(request.args['control_channel']))
                return str(response_value), 200
            
            
        @blueprint.route('/get_sensor', methods=['GET', 'POST'])
        def get_sensor():
            if request.method == 'POST':
                response_value = self.ls.get_sensor(str(request.json['control_channel']))
                return jsonify({'sensor': response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_sensor(str(request.args['control_channel']))
                return str(response_value), 200
            
        @blueprint.route('/get_setpoint', methods=['GET', 'POST'])
        def get_setpoint():
            if request.method == 'POST':
                response_value = self.ls.set_setpoint(int(request.json['control_loop']))
                return jsonify({'setpoint': response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_setpoint(int(request.args['control_loop']))
                return str(response_value), 200

        @blueprint.route('/get_heater_range', methods=['GET', 'POST'])
        def get_heater_range():
            sdict = {0: 'Off', 1: 'Low', 2: 'Medium', 3: 'High'}
            if request.method == 'POST':
                response_value = self.ls.get_heater_range(int(request.json['control_loop']))
                return jsonify({'range_index': response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_heater_range(int(request.args['control_loop']))
                return str(response_value), 200

        @blueprint.route('/get_heater_percent', methods=['GET', 'POST'])
        def get_heater_percent():
            if request.method == 'POST':
                response_value = self.ls.get_heater_percent(int(request.json['control_loop']))
                return jsonify({"percent": response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_heater_percent(int(request.args['control_loop']))
                return str(response_value), 200
    
        @blueprint.route('/get_heater_percent_fullrange', methods=['GET', 'POST'])
        def get_heater_percent_fullrange():
            if request.method == 'POST':
                response_value = self.ls.get_heater_percent_fullrange(int(request.json['control_loop']))
                return jsonify({"percent_fullrange": response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_heater_percent_fullrange(int(request.args['control_loop']))
                return str(response_value), 200
        
        @blueprint.route('/get_pid', methods=['GET', 'POST'])
        def get_pid():
            if request.method == 'POST':
                response_value = self.ls.get_PID(int(request.json['control_loop']))
                return jsonify({"P": response_value[0],
                                "I": response_value[1],
                                "D": response_value[2]}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_PID(int(request.args['control_loop']))
                return f'{response_value[0]:.2f}, {response_value[1]:.2f}, {response_value[2]:.2f}', 200
            
        @blueprint.route('/get_ramp_rate', methods=['GET', 'POST'])
        def get_ramp_rate():
            if request.method == 'POST':
                response_value = self.ls.get_ramp_rate(int(request.json['control_loop']))
                return jsonify({"ramp_rate": response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_ramp_rate(int(request.args['control_loop']))
                return str(response_value), 200
            
        @blueprint.route('/get_manual_output', methods=['GET', 'POST'])
        def get_manual_output():
            if request.method == 'POST':
                response_value = self.ls.get_manual_output(int(request.json['control_loop']))
                return jsonify({"manual_output": response_value}), 200
            elif request.method == 'GET':
                response_value = self.ls.get_manual_output(int(request.args['control_loop']))
                return str(response_value), 200
        
        @blueprint.route('/set_setpoint', methods=['GET', 'PUT', 'POST'])
        def set_setpoint():
            if request.method == 'POST':
                self.ls.set_setpoint(float(request.json['setpoint']),int(request.json['control_loop']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == "PUT":
                self.ls.set_setpoint(float(request.args['setpoint']),int(request.args['control_loop']))
                return str(""), 200
            
        @blueprint.route('/set_heater_range', methods=['GET', 'PUT', 'POST'])
        def set_heater_range():
            if request.method == 'POST':
                self.ls.set_heater_range(int(request.json['range_index']),int(request.json['control_loop']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                print(request.args)
                self.ls.set_heater_range(int(request.args['range_index']),int(request.args['control_loop']))
                return str(""), 200
            
        @blueprint.route('/set_pid', methods=['GET', 'PUT', 'POST'])
        def set_pid():
            if request.method == 'POST':
                self.ls.set_PID(float(request.json['P']),
                                float(request.json['I']),
                                float(request.json['D']),
                                int(request.json['control_loop']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ls.set_PID(float(request.args['P']),
                                float(request.args['I']),
                                float(request.args['D']),
                                int(request.args['control_loop']))
                return str(""), 200
            
        @blueprint.route('/set_ramp_rate', methods=['GET', 'PUT', 'POST'])
        def set_ramp_rate():
            if request.method == 'POST':
                self.ls.set_ramp_rate(float(request.json['ramp_rate']),int(request.json['control_loop']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == "PUT":
                self.ls.set_ramp_rate(float(request.args['ramp_rate']),int(request.args['control_loop']))
                return str(""), 200
            
        @blueprint.route('/set_manual_output', methods=['GET', 'PUT', 'POST'])
        def set_manual_output():
            if request.method == 'POST':
                self.ls.set_manual_output(float(request.json['manual_output']),int(request.json['control_loop']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == "PUT":
                self.ls.set_manual_output(float(request.args['manual_output']),int(request.args['control_loop']))
                return str(""), 200

        # Return blueprint to register in Flask app
        return blueprint
