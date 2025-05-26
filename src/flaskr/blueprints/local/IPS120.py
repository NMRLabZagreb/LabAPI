#!/usr/bin/env python

"""

This file defines a class for communicating with a local IPS120 device. The class a holds VISA resource as an attribute and links API calls to device module functions.
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
from ...modules.pyIPS120 import IPS120

# Blueprint is a global variable
blueprint = Blueprint('IPS120', __name__, url_prefix='/ips120')

class localIPS120():
    def __init__(self, device_present: bool = False):
        # Instantiate a VISA resource; IPS120 class implements various VISA queries as class methods
        self.ips = IPS120(device_present=device_present)
        
    # Authorization check
    @blueprint.before_request
    def check_api_key():
        if ('x-api-key' not in request.headers.keys(lower=True)) or (sha256(request.headers.get('X-API-Key').encode()).hexdigest() != API_KEY):
            return jsonify({'error': 'Unauthorized'}), 401
    
    def set_routes(self):
        '''
            A function to set API routes: in most cases API endpoint path == IPS120 class method.
            Most functions are boilerplate and can handle GET and POST methods.
        '''
        @blueprint.route('/connect', methods=['GET', 'PUT', 'POST'])
        def connect():
            self.ips.connect()
            if request.method == 'POST':
                return jsonify({}), 200
            elif request.method == 'GET':   
                return str(""), 200

        @blueprint.route('/query', methods=['GET', 'PUT', 'POST'])
        def query():
            if request.method == 'POST':
                response_value = self.ips.query(str(request.json['command']))
                return jsonify({'raw_response': response_value}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                response_value = self.ips.query(int(request.args['command']))
                return str(response_value), 200

        @blueprint.route('/write', methods=['GET', 'PUT', 'POST'])
        def write():
            if request.method == 'POST':
                self.ips.write(str(request.json['command']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.write(int(request.args['command']))
                return str(""), 200

        @blueprint.route('/get_output_current', methods=['GET', 'POST'])
        def get_output_current():
            response_value = self.ips.get_output_current()
            if request.method == 'POST':            
                return jsonify({'output_current': response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_magnet_current', methods=['GET', 'POST'])
        def get_magnet_current():
            response_value = self.ips.get_magnet_current()
            if request.method == 'POST':
                return jsonify({'magnet_current': response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_setpoint_current', methods=['GET', 'POST'])
        def get_setpoint_current():
            response_value = self.ips.get_setpoint_current()
            if request.method == 'POST':
                return jsonify({'setpoint_current': response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200

        @blueprint.route('/get_sweep_rate_current', methods=['GET', 'POST'])
        def get_sweep_rate_current():
            response_value = self.ips.get_sweep_rate_current()
            if request.method == 'POST':
                return jsonify({'sweep_rate_current': response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200

        @blueprint.route('/get_output_field', methods=['GET', 'POST'])
        def get_output_field():
            response_value = self.ips.get_output_field()
            if request.method == 'POST':
                return jsonify({"output_field": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
    
        @blueprint.route('/get_setpoint_field', methods=['GET', 'POST'])
        def get_setpoint_field():
            response_value = self.ips.get_setpoint_field()
            if request.method == 'POST':
                return jsonify({"setpoint_field": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
        
        @blueprint.route('/get_sweep_rate_field', methods=['GET', 'POST'])
        def get_sweep_rate_field():
            response_value = self.ips.get_sweep_rate_field()
            if request.method == 'POST':
                return jsonify({"sweep_rate_field": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_persistent_current', methods=['GET', 'POST'])
        def get_persistent_current():
            response_value = self.ips.get_persistent_current()
            if request.method == 'POST':
                return jsonify({"persistent_current": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_persistent_field', methods=['GET', 'POST'])
        def get_persistent_field():
            response_value = self.ips.get_persistent_field()
            if request.method == 'POST':
                return jsonify({"persistent_current": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_heater_current', methods=['GET', 'POST'])
        def get_heater_current():
            response_value = self.ips.get_heater_current()
            if request.method == 'POST':
                return jsonify({"heater_current": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_status', methods=['GET', 'POST'])
        def get_status():
            response_value = self.ips.get_status()
            if request.method == 'POST':
                return jsonify(response_value), 200
            elif request.method == 'GET':
                return '\n'.join([f'{key}: {value}' for key, value in response_value.items()]), 200
        
        @blueprint.route('/get_is_heater_on', methods=['GET', 'POST'])
        def get_is_heater_on():
            response_value = self.ips.get_is_heater_on()
            if request.method == 'POST':
                return jsonify({"is_heater_on": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_is_on_hold', methods=['GET', 'POST'])
        def get_is_on_hold():
            response_value = self.ips.get_is_on_hold()
            if request.method == 'POST':
                return jsonify({"is_on_hold": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_is_going_to_setpoint', methods=['GET', 'POST'])
        def get_is_going_to_setpoint():
            response_value = self.ips.get_is_going_to_setpoint()
            if request.method == 'POST':
                return jsonify({"is_going_to_setpoint": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_is_going_to_zero', methods=['GET', 'POST'])
        def get_is_going_to_zero():
            response_value = self.ips.get_is_going_to_zero()
            if request.method == 'POST':
                return jsonify({"is_going_to_zero": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/get_is_clamped', methods=['GET', 'POST'])
        def get_is_clamped():
            response_value = self.ips.get_is_clamped()
            if request.method == 'POST':
                return jsonify({"is_clamped": response_value}), 200
            elif request.method == 'GET':
                return str(response_value), 200
            
        @blueprint.route('/set_heater', methods=['GET', 'PUT', 'POST'])
        def set_heater():
            if request.method == 'POST':
                if request.json['value'] == 'on':
                    self.ips.set_heater_on()
                elif request.json['value'] == 'off':
                    self.ips.set_heater_off()
                else:
                    return jsonify({'error', 'unrecognized value'}), 200
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                if request.args['value'] == 'on':
                    self.ips.set_heater_on()
                elif request.args['value'] == 'off':
                    self.ips.set_heater_off()
                else:
                    return 'unrecognized value', 200
                return str(), 200
            
        @blueprint.route('/set_hold', methods=['GET', 'PUT', 'POST'])
        def set_hold():
            response_value = self.ips.set_hold()
            if request.method == 'POST':
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                return str(), 200
            
        @blueprint.route('/set_go_to_setpoint', methods=['GET', 'PUT', 'POST'])
        def set_go_to_setpoint():
            response_value = self.ips.set_go_to_setpoint()
            if request.method == 'POST':
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                return str(), 200
            
        @blueprint.route('/set_go_to_zero', methods=['GET', 'PUT', 'POST'])
        def set_go_to_zero():
            response_value = self.ips.set_go_to_zero()
            if request.method == 'POST':
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                return str(response_value), 200
            
        @blueprint.route('/set_clamped', methods=['GET', 'PUT', 'POST'])
        def set_clamped():
            response_value = self.ips.set_clamped()
            if request.method == 'POST':
                return jsonify({"is_clamped": response_value}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                return str(response_value), 200

        @blueprint.route('/set_setpoint_current', methods=['GET', 'PUT', 'POST'])
        def set_setpoint_current():
            if request.method == 'POST':
                self.ips.set_setpoint_current(float(request.json['setpoint_current']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.set_setpoint_current(float(request.args['setpoint_current']))
                return str(), 200
            
        @blueprint.route('/set_sweep_rate_current', methods=['GET', 'PUT', 'POST'])
        def set_sweep_rate_current():
            if request.method == 'POST':
                self.ips.set_sweep_rate_current(float(request.json['sweep_rate_current']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.set_sweep_rate_current(float(request.args['sweep_rate_current']))
                return str(), 200
            
        @blueprint.route('/set_setpoint_field', methods=['GET', 'PUT', 'POST'])
        def set_setpoint_field():
            if request.method == 'POST':
                self.ips.set_setpoint_field(float(request.json['setpoint_field']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.set_setpoint_field(float(request.args['setpoint_field']))
                return str(), 200
            
        @blueprint.route('/set_sweep_rate_field', methods=['GET', 'PUT', 'POST'])
        def set_sweep_rate_field():
            if request.method == 'POST':
                self.ips.set_sweep_rate_field(float(request.json['sweep_rate_field']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.set_sweep_rate_field(float(request.args['sweep_rate_field']))
                return str(), 200
            
        @blueprint.route('/set_magnet_field', methods=['GET', 'PUT', 'POST'])
        def set_magnet_field():
            if request.method == 'POST':
                self.ips.set_magnet_field(float(request.json['magnet_field']),
                                          float(request.json['ramp_rate']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.set_magnet_field(float(request.args['magnet_field']),
                                          float(request.args['ramp_rate']))
                return str(), 200
            
        @blueprint.route('/set_persistent_magnet_field', methods=['GET', 'PUT', 'POST'])
        def set_persistent_magnet_field():
            if request.method == 'POST':
                self.ips.set_persistent_magnet_field(float(request.json['magnet_field']),
                                                     float(request.json['ramp_rate']))
                return jsonify({}), 200
            elif request.method == 'GET' or request.method == 'PUT':
                self.ips.set_persistent_magnet_field(float(request.args['magnet_field']),
                                                     float(request.args['ramp_rate']))
                return str(), 200
            
        # Return blueprint to register in Flask app
        return blueprint
