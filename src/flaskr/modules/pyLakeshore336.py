#!/usr/bin/env python

"""

Wrapper for the serial (USB) communication with Keysight E5080A VNA.

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


import pyvisa as visa
import os
import configparser
from threading import Lock

class Lakeshore336:
    def __init__(self, address: str = None, device_present: bool = False) -> None:
        """
        Class to wrap communications with Lakeshore 336 temperature controller
            
        """
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(f'{path}/config.ini')
        self.device_in_use = Lock()

        # Handle resource address
        if address is not None:
            # Save configuration
            self.address = address
            config['Lakeshore336']['address'] = address
        else:
            if 'Lakeshore336' in config and 'address' in config['Lakeshore336']:
                self.address = config['Lakeshore336']['address']
            else:
                raise Exception('Resource address not provided!')

        self.device_present = device_present
        # Initialize communication
        self.connect()

    # Connector
    def connect(self):
        if self.device_present:
            self.rm = visa.ResourceManager()
        else:
            # Mock VISA
            self.rm = visa.ResourceManager(f'{os.path.dirname(__file__)}/pyvisa-sim.yaml@sim')
        # Initialize communication
        self.ls336 = self.rm.open_resource(self.address, read_termination = '\r\n', write_termination = '\r\n', query_delay=0.5)
        # Set non-typical parameters
        self.ls336.baud_rate = 57600
        self.ls336.data_bits = 7
        self.ls336.parity = visa.constants.Parity.odd

    # Query/Write functions to issue a direct query/write command and receive raw response
    def query(self, argument):
        with self.device_in_use:
            return self.ls336.query(argument)
            
    def write(self, argument):
        with self.device_in_use:
            self.ls336.write(argument)

    # SIMPLE GETTERS (one value) 
    def get_temperature(self, control_channel:str = 'A') -> float:
        """
        This method gets the current temperature [Kelvin] on channel control_channel.
        """        
        return float(self.query(f'KRDG? {control_channel}'))

    def get_sensor(self, control_channel:str = 'A') -> float:
        """
        This method gets the current sensor value (resistance) [Ohms].
        """
        return float(self.query(f'SRDG? {control_channel}'))
    
    def get_setpoint(self, control_loop:int = 2) -> float:
        """
        This method gets the active setpoint on control loop control_loop
        """       
        return float(self.query(f'SETP? {int(control_loop):d}'))
    
    def get_heater_range(self, control_loop:int = 2) -> int:
        """
        This method gets the heater range index: 0 Off, 1 Low, 2 Medium, 3 High.
        """
        return int(self.query(f'RANGE? {int(control_loop):d}')) or 0
    
    def get_heater_percent(self, control_loop:int = 2):
        """
        This method gets the heater output in percentage of the current range.
        """        
        return float(self.query(f'HTR? {int(control_loop):d}'))
    
    def get_heater_percent_fullrange(self, control_loop:int = 2):
        """
        This method gets the heater output in percentage of the total heater power.
        """
        heater_range = self.get_heater_range(int(control_loop))
        heater_percent = self.get_heater_percent(int(control_loop))

        # Max low is 1%, max medium is 10%, max high is 100%
        heater_fullrange = 0.001 * 10**heater_range
        return heater_percent*heater_fullrange

    def get_PID(self, control_loop:int = 2, pid = None) -> float:
        """
        This method gets the P, I, and D values for the control loop control_loop
        """       
        raw_response = self.query(f'PID? {int(control_loop):d}')
        response = [float(value) for value in raw_response.split(',')]
        response_mapping = {'P': 0, 'I': 1, 'D': 2}
        if pid is None:
            return response
        else:
            return response[response_mapping[pid]]

    def get_ramp_rate(self, control_loop:int = 2) -> float:
        """
        This method gets the ramp rate [K/min] for the control loop control_loop.
        """
        return float(self.query(f'RAMP? {int(control_loop):d}').split(',')[1])
    
    def get_manual_output(self, control_loop:int = 2) -> float:
        """
        This method gets the ramp rate [K/min] for the control loop control_loop.
        """
        return float(self.query(f'MOUT? {int(control_loop):d}'))

    # SIMPLE SETTERS
    def set_setpoint(self, setpoint:float, control_loop:int = 2):
        """
        This method sets the active setpoint on control loop control_loop
        """
        self.write(f'SETP {int(control_loop):d},{setpoint:.2f}')

    def set_heater_range(self, range_index: int, control_loop:int = 2):
        """
        This method sets the heater range given index: 0 Off, 1 Low, 2 Medium, 3 High.
        """
        self.write(f'RANGE {int(control_loop):d},{range_index:d}')

    def set_PID(self, P:float = None, I:float = None, D:float = None, control_loop:int = 2) :
        """
        This method gets the P, I, and D values for the control loop control_loop
        """
        current_pid = self.get_PID(control_loop)
        self.write(f'PID {int(control_loop):d},{(P or current_pid[0]):.1f},{(I or current_pid[1]):.1f},{(D or current_pid[2]):.1f}')

    def set_ramp_rate(self, ramp_rate:float, control_loop:int = 2):
        """
        This method sets the ramp rate [K/min] for the control loop control_loop.
        """
        if ramp_rate != 0:
            self.write(f'RAMP {int(control_loop):d},1,{ramp_rate:.2f}')
        else:
            # Turn off ramping
            self.write(f'RAMP {int(control_loop):d},0,0')

    def set_manual_output(self, manual_out:float, control_loop:int = 2):
        """
        This method gets the ramp rate [K/min] for the control loop control_loop.
        """
        self.write(f'MOUT {int(control_loop):d},{manual_out:.2f}')
