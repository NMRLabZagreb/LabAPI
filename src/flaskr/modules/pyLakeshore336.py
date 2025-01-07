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


class Lakeshore336:
    def __init__(self, address: str = None, device_present: bool = False) -> None:
        """
        Class to wrap communications with Lakeshore 336 temperature controller
            
        """
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(f'{path}/config.ini')

        # Handle resource address
        if address is not None:
            # Save configuration
            config['Lakeshore336']['address'] = address
        else:
            if 'Lakeshore336' in config and 'address' in config['Lakeshore336']:
                address = config['Lakeshore336']['address']
            else:
                raise Exception('Resource address not provided!')

        
        if device_present:
            self.rm = visa.ResourceManager()
        else:
            # Mock VISA
            self.rm = visa.ResourceManager(f'{path}/pyvisa-sim.yaml@sim')

        # Initialize communication
        self.ls336 = self.rm.open_resource(address, read_termination = '\n', write_termination = '\r\n')

    # SIMPLE GETTERS (one value) 
    def get_temperature(self, control_channel:str = 'A') -> float:
        """
        This method gets the current temperature [Kelvin] on channel control_channel.
        """        
        return float(self.ls336.query(f'KRDG? {control_channel}'))

    def get_sensor(self, control_channel:str = 'A') -> float:
        """
        This method gets the current sensor value (resistance) [Ohms].
        """
        return float(self.ls336.query(f'SRDG? {control_channel}'))
    
    def get_setpoint(self, control_loop:int = 1) -> float:
        """
        This method gets the active setpoint on control loop control_loop
        """       
        return float(self.ls336.query(f'SETP? {control_loop:d}'))
    
    def get_heater_range(self):
        """
        This method gets the heater range index: 0 Off, 1 Low, 2 Medium, 3 High.
        """
        return int(self.ls336.query(f'RANGE?'))
    
    def get_heater_percent(self):
        """
        This method gets the heater output in percentage of the current range.
        """        
        return float(self.ls336.query(f'HTR?'))
    
    def get_heater_percent_fullrange(self):
        """
        This method gets the heater output in percentage of the total heater power.
        """
        heater_range = self.get_heater_range()
        heater_percent = self.get_heater_percent()

        # Max low is 1%, max medium is 10%, max high is 100%
        heater_fullrange = 0.001 * 10**heater_range
        return heater_percent*heater_fullrange

    def get_PID(self, control_loop:int = 1) -> float:
        """
        This method gets the P, I, and D values for the control loop control_loop
        """       
        raw_response = self.ls336.query(f'PID? {control_loop:d}')
        return [float(value) for value in raw_response.split(',')]

    def get_ramp_rate(self, control_loop:int = 1) -> float:
        """
        This method gets the ramp rate [K/min] for the control loop control_loop.
        """
        return float(self.ls336.query(f'RAMP? {control_loop:d}'))
    
    def get_manual_output(self, control_loop:int = 1) -> float:
        """
        This method gets the ramp rate [K/min] for the control loop control_loop.
        """
        return float(self.ls336.query(f'MOUT? {control_loop:d}'))

    # SIMPLE SETTERS
    def set_setpoint(self, setpoint:float, control_loop:int = 1):
        """
        This method sets the active setpoint on control loop control_loop
        """
        self.ls336.write(f'SETP {control_loop:d},{setpoint:.2f}')

    def set_heater_range(self, range_index: int):
        """
        This method sets the heater range given index: 0 Off, 1 Low, 2 Medium, 3 High.
        """
        self.ls336.write(f'RANGE {range_index:d}')

    def set_PID(self, P:float, I:float, D:float, control_loop:int = 1) :
        """
        This method gets the P, I, and D values for the control loop control_loop
        """       
        self.ls336.write(f'PID {control_loop:d},{P:.2f},{I:.2f},{D:.2f}')

    def set_ramp_rate(self, ramp_rate:float, control_loop:int = 1):
        """
        This method sets the ramp rate [K/min] for the control loop control_loop.
        """
        if ramp_rate != 0:
            self.ls336.write(f'RAMP {control_loop:d},1,{ramp_rate:.2f}')
        else:
            # Turn off ramping
            self.ls336.write(f'RAMP {control_loop:d},0,0')

    def set_manual_output(self, manual_out:float, control_loop:int = 1):
        """
        This method gets the ramp rate [K/min] for the control loop control_loop.
        """
        self.ls336.write(f'MOUT {control_loop:d},{manual_out:.2f}')