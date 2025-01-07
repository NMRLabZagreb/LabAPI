#!/usr/bin/env python

"""

Tests for the serial (USB) communication with Lakeshore 336 temperature controller.

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
from pyLakeshore336 import Lakeshore336

class TestAllGetterTypes(unittest.TestCase):
    """
    Test all getters types
    """
    def setUp(self):
        self.ls336 = Lakeshore336()

    # SIMPLE GETTERS (one value)
    def test_get_temperature(self):
        return_value = self.ls336.get_temperature(control_channel=1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_sensor(self):
        return_value = self.ls336.get_sensor(control_channel=1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def test_get_setpoint(self):
        return_value = self.ls336.get_setpoint(control_loop=1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
        
    def test_get_heater_range(self):
        return_value = self.ls336.get_heater_range()
        self.assertIsInstance(return_value, int, f'Not an integer but {type(return_value)}')
    
    def test_get_heater_percent(self):
        return_value = self.ls336.get_heater_percent()
        self.assertIsInstance(return_value, int, f'Not a integer but {type(return_value)}')
    
    def test_get_heater_percent_fullrange(self):
        return_value = self.ls336.get_heater_percent_fullrange()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_PID(self):
        return_value = self.ls336.get_PID
        self.assertIsInstance(return_value, list, f'Not a list but {type(return_value)}')

    def test_get_ramp_rate(self):
        return_value = self.ls336.get_ramp_rate()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_manual_output(self):
        return_value = self.ls336.get_manual_output()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

class TestAllSetters(unittest.TestCase):
    """
    Test all setters
    """
    def setUp(self):
        self.ls336 = Lakeshore336()

    def test_set_setpoint(self):
        test_value = 281.
        self.ls336.set_setpoint(test_value, control_loop=1)
        self.assertEqual(self.ls336.get_setpoint(control_loop=1), test_value)

    def test_set_heater_range(self):
        test_value = 1
        self.ls336.set_heater_range(range_index=test_value)
        self.assertEqual(self.ls336.get_heater_range(), test_value)

    def test_set_PID(self):
        test_value = [10, 5, 2]
        self.ls336.set_PID(*test_value, control_loop=1)
        self.assertEqual(self.ls336.get_PID(control_loop=1), test_value)

    def test_set_ramp_rate(self):
        test_value = 2
        self.ls336.set_ramp_rate(test_value, control_loop=1)
        self.assertEqual(self.ls336.get_ramp_rate(control_loop=1), test_value)

    def test_set_manual_out(self):
        test_value = 5
        self.ls336.set_manual_output(test_value, control_loop=1)
        self.assertEqual(self.ls336.get_manual_output(control_loop=1), test_value)
        
if __name__=="__main__":
    unittest.main()
