#!/usr/bin/env python

"""

Wrapper for the parallel port communication with Nanotec stepper motor controllers (SMC11-2).

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

class NanotecSMC:
    def __init__(self, address: str = None, device_present: bool = True) -> None:
        """
        Class to wrap communications with Nanotec SMC11-2 controller(s)
            
        """
        self.path = os.path.dirname(__file__)
        self.config = configparser.ConfigParser()
        self.config.read(f'{self.path}/config.ini')

        # Handle resource address and configuration
        if address is not None:
            # Save configuration
            self.address = address
            self.config['NanotecSMC']['address'] = address
        else:
            if 'NanotecSMC' in self.config:
                    if 'address' in self.config['NanotecSMC']:
                        self.address = self.config['NanotecSMC']['address']
                    else:
                        raise Exception('Resource address not provided!')
                    # Parallel port bit offsets for tuning and matching stepper motors
                    self.bit_offset = {'tune': 0, 'match': 3}
                    self.min_delay = 1e-5 # 5 us
                    self.steps_per_turn = 200
                    if 'tune_offset' in self.config['NanotecSMC']:
                        self.bit_offset['tune'] = self.config['NanotecSMC']['tune_offset']
                    if 'match_offset' in self.config['NanotecSMC']:
                        self.bit_offset['match'] = self.config['NanotecSMC']['match_offset']
                    if 'min_delay' in self.config['NanotecSMC']:
                        self.min_delay = self.config['NanotecSMC']['min_delay']
                    if 'min_delay' in self.config['NanotecSMC']:
                        self.steps_per_turn = self.config['NanotecSMC']['steps_per_turn']

        # Initialize communication
        self.stop_flag = False
        self.thread_lock = threading.Lock()
        self.connect()

    # Connector
    def connect(self):
        self.smc = ParallelPort(self.address, self.thread_lock)

    # COMMANDS
    def make_n_steps(self, steps, seconds_per_turn, motor='tune'):
        direction_bit = self.bit_offset[motor]
        clock_bit = self.bit_offset[motor] + 1
        enable_bit = self.bit_offset[motor] + 2
        self.steps_remaining = abs(steps)
        step_delay = seconds_per_turn / self.steps_per_turn

        def __run__():
            self.stop_flag = False
            position = float(self.config['NanotecSMC'][f'{motor}_position'])
            # Enable motor
            self.smc.set_data_low(enable_bit)
            while not self.stop_flag and self.steps_remaining:
                # Precise step timing
                start_timer = time.perf_counter()
                # Make a step
                self.smc.set_data_low(clock_bit)
                time.sleep(self.min_delay)
                self.smc.set_data_low(direction_bit) if steps > 0 else self.smc.set_data_high(direction_bit)
                time.sleep(self.min_delay)
                self.smc.set_data_high(clock_bit)
                time.sleep(self.min_delay)
                self.smc.set_data_low(clock_bit)
                time.sleep(self.min_delay)
                # Make note of motor position
                self.steps_remaining -= 1
                position += (1 if steps > 0 else -1)
                if position <= 0:
                    self.stop_flag = True
                # Step delay
                while (time.perf_counter()-start_timer) < step_delay:
                    time.sleep(self.min_delay)
            # Disable motor
            self.smc.set_data_high(enable_bit)
            self.config['NanotecSMC'][f'{motor}_position'] = f'{position:.1f}'
            
        thread = threading.Thread(target=__run__)
        thread.start()
        thread.join()
        with open(f'{self.path}/config.ini', 'w') as configfile:
            self.config.write(configfile)

    def get_position(self, motor='tune'):
        return float(self.config['NanotecSMC'][f'{motor}_position'])
    
    def stop_all(self):
        self.stop_flag = True
