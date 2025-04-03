#!/usr/bin/env python

"""

Wrapper for the serial (USB) communication with Oxford's Intelligent Power Supply (IPS) for 12T magnet.

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
import re
import time

class IPS120:
    def __init__(self, address: str = None, device_present: bool = False) -> None:
        """
        Class to wrap communications with IPS120 magnet power supply
            
        """
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(f'{path}/config.ini')

        # Handle resource address
        if address is not None:
            # Save configuration
            self.address = address
            config['IPS120']['address'] = address
        else:
            if 'IPS120' in config and 'address' in config['IPS120']:
                self.address = config['IPS120']['address']
            else:
                raise Exception('Resource address not provided!')

        # Test a connection
        self.device_present = device_present
        self.check_and_reset_communication()

        # Define status codes
        self.system_status_m = {0: 'Normal',
                                1: 'Quenched',
                                2: 'Overheated',
                                4: 'Warming up',
                                8: 'Fault'}
        self.system_status_n = {0: 'Normal',
                                1: 'On positive voltage limit',
                                2: 'On negative voltage limit',
                                4: 'Outside negative current limit',
                                8: 'Outside positive current limit'}
        self.activity_status = {0: 'Hold',
                                1: 'To setpoint',
                                2: 'To zero',
                                4: 'Clamped'}
        self.heater_status = {0: 'Off, magnet at zero',
                              1: 'On',
                              2: 'Off, magnet at field',
                              5: 'Heater fault',
                              8: 'No switch present'}
        
    # Connector
    def connect(self):
        if self.device_present:
            self.rm = visa.ResourceManager()
        else:
            # Mock VISA
            self.rm = visa.ResourceManager(f'{os.path.dirname(__file__)}/pyvisa-sim.yaml@sim')
        # Initialize communication
        self.ips = self.rm.open_resource(self.address, read_termination = '\r\n', write_termination = '\r\n')
        # Set non-typical parameters
        # Set termination to /r/n
        self.ips.write('Q2')

    # Test connection to the device and reconnect if necessary
    def check_and_reset_communication(self):
        retries = 5
        connected = False
        while not connected and retries:
            try:
                self.connect()
                if self.ips.query('V') != '':
                    connected = True
            except:
                # If connection fails try again 
                retries -= 1

    # Query/Write functions check the communication before querying the device
    def query(self, argument):
        self.check_and_reset_communication()
        return self.ips.query(argument)

    def write(self, argument):
        self.check_and_reset_communication()
        self.ips.write(argument)


    # SIMPLE GETTERS (one value)
    def get_output_current(self) -> float:
        """
        This method gets the current output current.
        """
        return float(self.query('R 0').strip('R'))
    
    def get_magnet_current(self) -> float:
        """
        This method gets the current magnet current.
        """
        return float(self.query('R 2').strip('R'))
        
    def get_setpoint_current(self) -> float:
        """
        This method gets the current target current.
        """
        return float(self.query('R 5').strip('R'))
        
    def get_sweep_rate_current(self) -> float:
        """
        This method gets the current sweep rate in amp/minute.
        """
        return float(self.query('R 6').strip('R'))
    
    def get_output_field(self) -> float:
        """
        This method gets the output field (in sweep) in Teslas.
        """
        return float(self.query('R 7').strip('R'))
        
    def get_setpoint_field(self) -> float:
        """
        This method gets the target field (setpoint) in Teslas.
        """
        return float(self.query('R 8').strip('R'))
    
    def get_sweep_rate_field(self) -> float:
        """
        This method gets the field sweep rate Tesla/min.
        """
        return float(self.query('R 9').strip('R'))
        
    def get_persistent_current(self) -> float:
        """
        This method gets the persistent current (no sweeping) in Amps.
        """
        return float(self.query('R 16').strip('R'))
    
    def get_persistent_field(self) -> float:
        """
        This method gets the persistent field (no sweeping) in Teslas.
        """
        return float(self.query('R 18').strip('R'))
    
    def get_heater_current(self) -> float:
        """
        This method gets the heater current in miliAmps.
        """
        return float(self.query('R 20').strip('R'))
    
    #STATUS STRING HANDLING
    def get_status(self) -> str:
        """
        This method reads the IPS status string and returs list of 9 integers.
        Each integer represents a status of a different subsystem (consult IPS manual for more details)
        """
        response_raw = self.query('X')
        response_pattern = re.compile(r'X(\d)(\d)A(\d)C(\d)H(\d)M(\d)(\d)P(\d)(\d)')
        response = [int(r) for r in response_pattern.search(response_raw).groups()]

        system_status = f'{self.system_status_m[response[0]]}, {self.system_status_n[response[1]]}'
        activity_status = self.activity_status[response[2]]
        heater_status = self.heater_status[response[4]]

        return {'system_status': system_status,
                'activity_status': activity_status,
                'heater_status': heater_status}
    
    def get_is_heater_on(self) -> bool:
        """
        This method returns a bool value if the heater is turned on.
        """
        return self.get_status()['heater_status'] == 'On'

    def get_is_on_hold(self) -> bool:
        """
        This method returns a bool value if the IPS is on hold
        """
        return self.get_status()['activity_status'] == 'Hold'
    
    def get_is_going_to_setpoint(self) -> bool:
        """
        This method returns a bool value is the IPS going to setpoint.
        """
        return self.get_status()['activity_status'] == 'To setpoint'
    
    def get_is_going_to_zero(self) -> bool:
        """
        This method returns a bool value is the IPS going to zero.
        """
        return self.get_status()['activity_status'] == 'To zero'
    
    def get_is_clamped(self) -> bool:
        """
        This method checks whether the output is clamped.
        """
        return self.get_status()['activity_status'] == 'Clamped'
    
    # SIMPLE SETTERS
    def set_hold(self):
        """
        This method sends the HOLD command.
        """
        self.query('C1')
        self.query('A0')
        self.query('C0')

    def set_go_to_setpoint(self):
        """
        This method sends the GO TO SETPOINT command.
        """
        self.query('C1')
        self.query('A1')
        self.query('C0')

    def set_go_to_zero(self):
        """
        This method sends the GO TO ZERO command.
        """
        self.query('C1')
        self.query('A2')
        self.query('C0')
    
    def set_clamped(self):
        """
        This method clamps the output.
        """
        self.query('C1')
        self.query('A4')
        self.query('C0')

    def set_heater_off(self):
        """
        This method turns off the heater.
        """
        self.query('C1')
        self.query('H0')
        self.query('C0')

    def set_heater_on(self):
        """
        This method turns on the heater.
        """
        self.query('C1')
        self.query('H1')
        self.query('C0')
        
    def set_setpoint_current(self, setpoint_current: float):
        """
        This method sets the current [Amps] setpoint. Current can be negative and the method
        will handle the polarity change.
        """
        self.query('C1')
        self.query(f'I{setpoint_current:.3f}')
        self.query('C0')
        self.ips.clear()

    def set_setpoint_field(self, setpoint_field: float):
        """
        This method set the field [Tesla] setpoint. Field can be negative and the method
        will handle the polarity change.
        """
        self.query('C1')
        self.query(f'J{setpoint_field:.4f}')
        self.query('C0')

    def set_sweep_rate_current(self, sweep_rate: float):
        """
        This method set the current sweep rate [Amps/min].
        """
        self.query('C1')
        self.query(f'S{abs(sweep_rate):.2f}')
        self.query('C0')

    def set_sweep_rate_field(self, sweep_rate: float):
        """
        This method set the field sweep rate [Teslas/min].
        """
        self.query('C1')
        self.query(f'T{abs(sweep_rate):.3f}')
        self.query('C0')

    ### HIGHER LEVEL COMMANDS ###
    def set_magnet_field(self, magnet_field: float, ramp_rate: float = None):
        """
        This method changes the field in magnet but does NOT go to persistent mode. This method can be used for
        field-sweep measurements.
        """
        if ramp_rate:
            self.set_sweep_rate_field(ramp_rate)
        time.sleep(1)

        # Go to the current field and turn on heater
        if self.get_persistent_field() != self.get_output_field() and not self.get_is_heater_on():
            self.set_setpoint_field(self.get_persistent_field)
            self.set_go_to_setpoint()
            while self.get_persistent_field() != self.get_output_field():
                time.sleep(5)
            self.set_hold()
            self.set_heater_on()
            time.sleep(60)

        # Go to setpoint field
        self.set_setpoint_field(magnet_field)
        self.set_go_to_setpoint()
        while self.get_output_field() != self.get_setpoint_field():
            time.sleep(5)
        self.set_hold()

    def set_persistent_magnet_field(self, magnet_field: float, ramp_rate: float = None):
        """
        This method changes the field in magnet and enters persistent mode.
        """
        current_field = self.get_persistent_field()
        current_setpoint = -10000
        while abs(current_setpoint - magnet_field) > 0.05:
            current_setpoint = magnet_field - (current_field - magnet_field) / 2
            self.set_magnet_field(magnet_field, ramp_rate)
            current_field = self.get_output_field()
            time.sleep(1)
        self.set_magnet_field(magnet_field)
        self.set_heater_off()
        time.sleep(60)
        self.set_go_to_zero()
        self.set_hold()
        self.set_clamped()
