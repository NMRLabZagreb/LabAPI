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
import time

class KeysightE5080A:
    def __init__(self, address: str = None, device_present: bool = False) -> None:
        """
        Class to wrap communications with Keysight ENA E5080A network analyser
            
        """
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(f'{path}/config.ini')

        # since Python 3.8 Agilent visa32.dll fails to load because it cannot find its .dll dependencies.
        # These two folders should be added manually to the search path
        if os.path.exists(config['KeysightE5080A']['x86_dll']) and os.path.exists(config['KeysightE5080A']['x64_dll']):
            os.add_dll_directory(config['KeysightE5080A']['x86_dll'])
            os.add_dll_directory(config['KeysightE5080A']['x64_dll'])

        # Handle resource address
        if address is not None:
            # Save configuration
            self.address = address
            config['KeysightE5080A']['address'] = address
        else:
            if 'KeysightE5080A' in config and 'address' in config['KeysightE5080A']:
                self.address = config['KeysightE5080A']['address']
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
        self.VNA = self.rm.open_resource(self.address, read_termination = '\r\n', write_termination = '\r\n')
        # Set non-typical parameters
        self.VNA.write(':CALC1:PAR:SEL "CH1_S11_1"')

    # Query/Write functions to issue a direct query/write command and receive raw response
    def query(self, argument):
        try:
            return self.VNA.query(argument)
        except Exception as e:
            print(e)
            return ""

    def write(self, argument):
        try:
            return self.VNA.write(argument)
        except Exception as e:
            print(e)
            return ""

    # SIMPLE GETTERS (one value)
    def get_marker_X(self, marker_index: int) -> float:
        """
        Gets the position [in MHz] Marker [marker_index]
        """
        self.write(f':CALC1:MARK{marker_index} ON')
        return float(self.query(f':CALC1:MARK{marker_index}:X?'))/1000000 

    def get_marker_Y(self, marker_index: int) -> float:
        """
        Gets the S11 value [in dB] for Marker [marker_index]
        """
        self.write(f':CALC1:MARK{marker_index} ON')
        return float(self.query(f':CALC1:MARK{marker_index}:Y?').split(',')[0])
    
    def get_marker_Y_at(self, marker_index: int, frequency: float) -> float:
        """
        Sets the position [in MHz] of a Marker [marker_index] and then returns its S11 value.
        """
        self.set_marker_X(marker_index, frequency)
        return float(self.get_marker_Y(marker_index))
        
    def get_minimum(self, marker_index: int) -> float:
        """
        Gets the position [in MHz] of the S11 minimum in current sweep range
        """
        self.write(f':CALC1:MARK{marker_index}:FUNC:EXEC MIN')
        return self.get_marker_X(marker_index)
    
    def get_sweep_points(self) -> int:
        """
        Get the number of sweep points
        """
        return int(self.query(f':SENS1:SWE:POIN?'))
    
    def get_Q(self, marker_index: int) -> float:
        """
        Returns "the NMR Q-value" measured at 13 dB.
        """
        # Center frequency
        frequency = self.get_minimum(marker_index)
        self.write(f':SENS1:FREQ:CENT {frequency*1e6:.0f}')

        # Turn on bandwidth search and set threshold to 13 dB
        self.write(f':CALC1:MEAS1:MARK{marker_index}:NOTC ON')
        self.write(f':CALC1:MEAS1:MARK{marker_index}:NOTC:REF PEAK')
        self.write(f':CALC1:MEAS1:MARK{marker_index}:NOTC:THR -13')

        # Query and return the data
        data = self.query(f':CALC1:MEAS1:MARK{marker_index}:NOTC:DATA?')
        self.write(f':CALC1:MEAS1:MARK{marker_index}:NOTC OFF')
        return float(data.strip('\n').split(',')[2])
    
    # COMPLEX GETTERS (list of values)
    def get_sweep_range(self) -> list:
        """
        Gets the sweep range [in MHz]
        """
        start = float(self.query(':SENS1:FREQ:STAR?'))/1e6
        stop = float(self.query(':SENS1:FREQ:STOP?'))/1e6
        return start, stop

    def get_filter(self, marker_index: int, threshold: float = 0.5) -> list:
        """
        Gets the filter data [bandwidth, center, Q value, insertion loss] for a Marker [marker_index].
        """        
        # Center frequency
        frequency = self.get_minimum(marker_index)
        self.write(f':SENS1:FREQ:CENT {frequency*1e6:.0f}')

        # Set display format to linear
        self.write(':CALC1:FORM MLIN')
        
        # Turn on bandwidth search and set threshold to half-maximum
        value = self.get_marker_Y_at(marker_index, frequency)
        self.write(f':CALC1:MEAS1:MARK{marker_index}:BWID ON')
        self.write(f':CALC1:MEAS1:MARK{marker_index}:BWID:THR {(1-value)/2:.2f}')

        # Query and return the data
        data = self.query(f':CALC1:MEAS1:MARK{marker_index}:BWID:DATA?')

        # Reset display format
        self.write(f':CALC1:MEAS1:MARK{marker_index}:BWID OFF')
        self.write(':CALC1:FORM MLOG')
        return [float(value) for value in data.strip('\n').split(',')]
    
    def get_complex_data(self) -> list:
        """
        Reads corrected data from the CALC1. Output data is formatted as (Freq, Complex)
        """
        # Find range and number of points to construct a list of frequencies
        start, stop = self.get_sweep_range()
        points = self.get_sweep_points()
        frequencies = [start+i*(stop-start)/(points-1) for i in range(points)]

        # VNA returns data as string "real,imag,real,imag,...", format it and return
        raw_data = self.query(':CALC1:MEAS1:DATA:SDAT?').split(',')
        complex_data = [float(raw_data[2*i])+float(raw_data[2*i+1])*1j for i in range(points)]
        return list(zip(frequencies, complex_data))     

    # SETTERS
    def set_marker_X(self, marker_index: int, frequency: float):
        """
        Sets the frequency [in MHz] of a Marker [marker_index]
        """
        self.write(f':CALC1:MARK{marker_index}:X {frequency*1e6:.0f}')

    def set_sweep_points(self, points: int):
        """
        Set the number of sweep points
        """
        self.write(f':SENS1:SWE:POIN {points:d}')

    def set_sweep_range(self, start, stop):
        """
        Sets the sweep range [in MHz]
        """
        self.write(f':SENS1:FREQ:STAR {start*1e6:.0f}')
        self.write(f':SENS1:FREQ:STOP {stop*1e6:.0f}')

if __name__=="__main__":
    ks = KeysightE5080A()
