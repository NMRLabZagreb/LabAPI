#!/usr/bin/env python

"""

Wrapper for the serial (USB) communication with Oxford's Intelligent Level Meter (ILM).

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

class ILM:
    def __init__(self, address: str = None, device_present: bool = False) -> None:
        """
        Class to wrap communications with ILM magnet power supply
            
        """
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(f'{path}/config.ini')

        # Handle resource address
        if address is not None:
            # Save configuration
            self.address = address
            config['ILM']['address'] = address
        else:
            if 'ILM' in config and 'address' in config['ILM']:
                self.address = config['ILM']['address']
            else:
                raise Exception('Resource address not provided!')

        # Test a connection
        self.device_present = device_present
        self.connect()
        
    # Connector
    def connect(self):
        if self.device_present:
            self.rm = visa.ResourceManager()
        else:
            # Mock VISA
            self.rm = visa.ResourceManager(f'{os.path.dirname(__file__)}/pyvisa-sim.yaml@sim')
        # Initialize communication
        self.ilm = self.rm.open_resource(self.address, read_termination = '\r\n', write_termination = '\r\n')
        # Set non-typical parameters
        # Set termination to /r/n
        self.ilm.write('Q2')

    # Query/Write functions to issue a direct query/write command and receive raw response
    def query(self, argument):
        return self.ilm.query(argument)

    def write(self, argument):
        self.ilm.write(argument)


    # SIMPLE GETTERS (one value)
    def get_LHe_level(self) -> float:
        """
        This method gets the current liquid helium level.
        """
        while True:
            try:
                return float(self.query('R 1').strip('R'))/10
            except:
                pass
    
    def get_LN2_level(self) -> float:
        """
        This method gets the current liquid nitrogen level.
        """
        while True:
            try:
                return float(self.query('R 2').strip('R'))/10
            except:
                pass
