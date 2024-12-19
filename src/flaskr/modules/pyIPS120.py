#!/usr/bin/env python

"""

Wrapper for the serial (USB) communication with Oxford's Intelligent Power Supply (IPS) for 12T magnet.

"""

__author__ = "Ivan Jakovac"
__email__ = "ivan.jakovac2@gmail.com"
__version__ = "v0.1"

#  Copyright (C) 2020-2022 Ivan Jakovac
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
            config['IPS120']['address'] = address
        else:
            if 'IPS120' in config and 'address' in config['IPS120']:
                address = config['IPS120']['address']
            else:
                raise Exception('Resource address not provided!')

        
        if device_present:
            self.rm = visa.ResourceManager()
        else:
            # Mock VISA
            self.rm = visa.ResourceManager(f'{path}/pyvisa-sim.yaml@sim')

        # Initialize communication
        self.ips = self.rm.open_resource(address, read_termination = '\n', write_termination = '\r\n')
        # Set control to remote & unlocked
        self.ips.write('C3')

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

    # SIMPLE GETTERS (one value)
    def get_output_current(self) -> float:
        """
        This method gets the current output current.
        """
        return float(self.ips.query('R 0'))
    
    def get_magnet_current(self) -> float:
        """
        This method gets the current magnet current.
        """
        return float(self.ips.query('R 2'))
        
    def get_setpoint_current(self) -> float:
        """
        This method gets the current target current.
        """
        return float(self.ips.query('R 5'))
        
    def get_sweep_rate_current(self) -> float:
        """
        This method gets the current sweep rate in amp/minute.
        """
        return float(self.ips.query('R 6'))
    
    def get_output_field(self) -> float:
        """
        This method gets the output field (in sweep) in Teslas.
        """
        return float(self.ips.query('R 7'))
        
    def get_setpoint_field(self) -> float:
        """
        This method gets the target field (setpoint) in Teslas.
        """
        return float(self.ips.query('R 8'))
    
    def get_sweep_rate_field(self) -> float:
        """
        This method gets the field sweep rate Tesla/min.
        """
        return float(self.ips.query('R 9'))
        
    def get_persistent_current(self) -> float:
        """
        This method gets the persistent current (no sweeping) in Amps.
        """
        return float(self.ips.query('R 16'))
    
    def get_persistent_field(self) -> float:
        """
        This method gets the persistent field (no sweeping) in Teslas.
        """
        return float(self.ips.query('R 18'))
    
    def get_heater_current(self) -> float:
        """
        This method gets the heater current in miliAmps.
        """
        return float(self.ips.query('R 20'))
    
    #STATUS STRING HANDLING
    def get_status(self) -> str:
        """
        This method reads the IPS status string and returs list of 9 integers.
        Each integer represents a status of a different subsystem (consult IPS manual for more details)
        """
        response_raw = self.ips.query('X')
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
        self.ips.write('A0')

    def set_go_to_setpoint(self):
        """
        This method sends the GO TO SETPOINT command.
        """
        self.ips.write('A1')

    def set_go_to_zero(self):
        """
        This method sends the GO TO ZERO command.
        """
        self.ips.write('A2')
    
    def set_clamped(self):
        """
        This method clamps the output.
        """
        self.ips.write('A4')

    def set_heater_off(self):
        """
        This method turns off the heater.
        """
        self.ips.write('H0')

    def set_heater_on(self):
        """
        This method turns on the heater.
        """
        self.ips.write('H1')

    def set_setpoint_current(self, setpoint_current: float):
        """
        This method sets the current [Amps] setpoint. Current can be negative and the method
        will handle the polarity change.
        """
        if setpoint_current > 0:
            self.ips.write('P1')
            self.ips.write(f'I{setpoint_current:.3f}')
        else:
            self.ips.write('P2')
            self.ips.write(f'I{setpoint_current:.3f}')

    def set_setpoint_field(self, setpoint_field: float):
        """
        This method set the field [Tesla] setpoint. Field can be negative and the method
        will handle the polarity change.
        """
        if setpoint_field > 0:
            self.ips.write('P1')
            self.ips.write(f'J{setpoint_field:.4f}')
        else:
            self.ips.write('P2')
            self.ips.write(f'J{setpoint_field:.4f}')

    def set_sweep_rate_current(self, sweep_rate: float):
        """
        This method set the current sweep rate [Amps/min].
        """
        self.ips.write(f'S{sweep_rate:.2f}')

    def set_sweep_rate_field(self, sweep_rate: float):
        """
        This method set the field sweep rate [Teslas/min].
        """
        self.ips.write(f'T{sweep_rate:.3f}')

    ### HIGHER LEVEL COMMANDS ###
    def go_to_current_field(self):
        """
        This method sets the output current/field to the persistent current/field and turns on the heater
        """
        # Ensure the heater is OFF, and we are on HOLD
        if self.get_persistent_field() == self.get_output_field():
            self.set_heater_off()
        if not self.get_is_on_hold():
            self.set_hold()

        # Get the current field and set setpoint
        current_field = self.get_persistent_field()
        self.set_setpoint_field(current_field)

        # Go to current setpoint
        self.set_go_to_setpoint()
        while self.get_output_field() != current_field:
            time.sleep(1)
        
        # Turn on the heater
        self.set_hold()
        self.set_heater_on() # Heater ON checks if IPS == magnet
        time.sleep(60)
    
    def go_to_persistent_mode(self):
        """
        This method turns off the heater and lowers the output current to zero (persistent mode).
        """
        # Wait for output to reach the setpoint
        while self.get_output_field() != self.get_setpoint_field:
            time.sleep(1)

        # Check is output/setpoint is equal to the persistent field before
        # turning off the heater
        if self.get_output_field() == self.get_persistent_field():
            # Turn off the heater
            self.set_hold()
            self.set_heater_off()
            time.sleep(60)

            # Go to persistent mode and clamp the output
            self.set_go_to_zero()
            while self.get_output_field != 0:
                time.sleep(1)
            self.set_clamped()

    def set_magnet_field(self, magnet_field: float, ramp_rate: float = None):
        """
        This method changes the field in magnet but does NOT go to persistent mode. This method can be used for
        field-sweep measurements.
        """
        if ramp_rate:
            self.set_sweep_rate_field(ramp_rate)

        # Go to the current field
        if self.get_persistent_field() != self.get_output_current() and not self.get_is_heater_on():
            self.go_to_current_field()

        # Go to setpoint field
        self.set_setpoint_field(magnet_field)
        self.set_go_to_setpoint()
        while self.get_output_field() != magnet_field:
            time.sleep(1)

    def set_persistent_magnet_field(self, magnet_field: float, ramp_rate: float = None):
        """
        This method changes the field in magnet and enters persistent mode.
        """
        self.set_magnet_field(magnet_field, ramp_rate)
        self.go_to_persistent_mode()