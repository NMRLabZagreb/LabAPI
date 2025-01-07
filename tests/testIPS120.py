#!/usr/bin/env python

"""

Tests for the serial (USB) communication with IPS120 power supply.

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

import unittest
import sys
sys.path.append('../src/flaskr/modules')
from pyIPS120 import IPS120

class TestAllGetterTypes(unittest.TestCase):
    """
    Test all getters types
    """
    def setUp(self):
        self.ips = IPS120()

    # SIMPLE GETTERS (one value)
    def test_get_output_current(self):
        return_value = self.ips.get_output_current()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_magnet_current(self):
        return_value = self.ips.get_magnet_current()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def test_get_setpoint_current(self):
        return_value = self.ips.get_setpoint_current()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
        
    def test_get_sweep_rate_current(self):
        return_value = self.ips.get_sweep_rate_current()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_output_field(self):
        return_value = self.ips.get_output_field()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def test_get_setpoint_field(self):
        return_value = self.ips.get_setpoint_field()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
        
    def test_get_sweep_rate_field(self):
        return_value = self.ips.get_sweep_rate_field()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def test_get_persistent_current(self):
        return_value = self.ips.get_persistent_current()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_persistent_field(self):
        return_value = self.ips.get_persistent_field()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_heater_current(self):
        return_value = self.ips.get_heater_current()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def test_get_status(self):
        return_value = self.ips.get_status()
        self.assertIsInstance(return_value, str, f'Not a string but {type(return_value)}')

class TestNonActiveSetters(unittest.TestCase):
    """
    Test setters which do not change the field or current.
    """
    def setUp(self):
        self.ips = IPS120()

    def test_set_setpoint_current(self):
        test_value = 10.5
        self.ips.set_setpoint_current(setpoint_current=test_value)
        self.assertEqual(self.ips.get_setpoint_current(), test_value)

    def test_set_setpoint_field(self):
        test_value = -3.5
        self.ips.set_setpoint_field(setpoint_field=test_value)
        self.assertEqual(self.ips.get_setpoint_field(), test_value)

    def test_set_sweep_rate_current(self):
        test_value = 0.1
        self.ips.set_sweep_rate_current(sweep_rate=test_value)
        self.assertEqual(self.ips.get_sweep_rate_current(), test_value)

    def test_set_sweep_rate_field(self):
        test_value = 0.05
        self.ips.set_sweep_rate_current(sweep_rate=test_value)
        self.assertEqual(self.ips.get_sweep_rate_field(), test_value)
        
if __name__=="__main__":
    unittest.main()
