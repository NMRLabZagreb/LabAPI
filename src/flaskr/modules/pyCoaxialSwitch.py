#!/usr/bin/env python

"""

Wrapper for the parallel port communication with Teledyne Coaxial Switch.

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

import os
import configparser
import time
import threading
from .pyParallel import ParallelPort

class CoaxialSwitch:
    def __init__(self, address: str = None, device_present: bool = True) -> None:
        """
        Class to wrap communications with Teledyne Coaxial Switch
            
        """
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(f'{path}/config.ini')

        # Handle resource address and configuration
        if address is not None:
            # Save configuration
            self.address = address
            config['CoaxialSwitch']['address'] = address
        else:
            if 'CoaxialSwitch' in config:
                    if 'address' in config['CoaxialSwitch']:
                        self.address = config['CoaxialSwitch']['address']
                    else:
                        raise Exception('Resource address not provided!')
                    # Parallel port bit offsets for tuning and matching stepper motors
                    self.bits = {'spectro': 6, 'vna': 7}
                    if 'spectro' in config['CoaxialSwitch']:
                        self.bits['spectro'] = config['CoaxialSwitch']['spectro']
                    if 'vna' in config['CoaxialSwitch']:
                        self.bits['vna'] = config['CoaxialSwitch']['vna']

        # Initialize communication
        self.thread_lock = threading.Lock()
        self.connect()

    # Connector
    def connect(self):
        self.switch = ParallelPort(self.address, self.thread_lock)

    # GETTERS
    def get_switch(self):
        # VNA is normally open
        if self.switch.get_data(self.bits['vna']):
            return 'vna'
        else:
            return 'spectro'

    # SETTERS
    def set_switch(self, to='spectro'):
        if to == 'spectro':
            self.switch.set_data_low(self.bits['vna'])
            self.switch.set_data_high(self.bits['spectro'])
        elif to == 'vna':
            self.switch.set_data_low(self.bits['spectro'])
            self.switch.set_data_high(self.bits['vna'])
            

    
