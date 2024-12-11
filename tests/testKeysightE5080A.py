#!/usr/bin/env python

"""

Unit tests for the serial (USB) communication with Keysight E5080A VNA.

"""

__author__ = "Ivan Jakovac"
__email__ = "ivan.jakovac2@gmail.com"
__version__ = "api_v0.1"


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

import unittest
import sys
sys.path.append('../src/modules')
from pyKeysightE5080A import KeysightE5080A

class TestAllGetterTypes(unittest.TestCase):
    """
    Test all getters types
    """
    def setUp(self):
        self.VNA = KeysightE5080A()

    # SIMPLE GETTERS (one value)
    def get_marker_X(self):
        return_value = self.VNA.get_marker_X(marker_index = 1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def get_marker_Y(self):
        return_value = self.VNA.get_marker_Y(marker_index = 1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def get_marker_Y_at(self):
        return_value = self.VNA.get_marker_Y_at(marker_index = 1, frequency = 10)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
        
    def get_minimum(self):
        return_value = self.VNA.get_minimum(marker_index = 1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')
    
    def get_sweep_points(self):
        return_value = self.VNA.get_sweep_points()
        self.assertIsInstance(return_value, int, f'Not a integer but {type(return_value)}')
    
    def get_Q(self):
        return_value = self.VNA.get_Q(marker_index = 1)
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    # COMPLEX GETTERS (list of values)
    def get_sweep_range(self) -> list:
        return_value = self.VNA.get_sweep_range()
        self.assertIsInstance(return_value), list, f'Not a built-in list but {type(return_value)}'
        self.assertIsInstance(return_value[0], float, f'Start value not a float but {type(return_value[0])}')
        self.assertIsInstance(return_value[1], float, f'Stop value not a float but {type(return_value[1])}')

    def get_filter(self):
        return_value = self.VNA.get_filter(marker_index = 1)
        self.assertIsInstance(return_value), list, f'Not a built-in list but {type(return_value)}'
        self.assertIsInstance(return_value[0], float, f'Bandwidth value not a float but {type(return_value[0])}')
        self.assertIsInstance(return_value[1], float, f'Center value not a float but {type(return_value[1])}')
        self.assertIsInstance(return_value[2], float, f'Q-factor value not a float but {type(return_value[2])}')
        self.assertIsInstance(return_value[3], float, f'Insertion loss value not a float but {type(return_value[3])}')
    
    def get_complex_data(self):
        return_value = self.VNA.get_complex_data()
        self.assertIsInstance(return_value), list, f'Not a built-in list but {type(return_value)}'
        self.assertIsInstance(return_value[0], list, f'First element is a built-in list (frequency-data pair) but {type(return_value[0])}')
        self.assertIsInstance(return_value[0][0], float, f'Frequency value not a float but {type(return_value[0][0])}')
        self.assertIsInstance(return_value[0][1], complex, f'Data value not a complex but {type(return_value[0][1])}')

class TestAllSetters(unittest.TestCase):
    """
    Test all setters
    """
    def setUp(self):
        self.VNA = KeysightE5080A()

    def set_marker_X(self):
        test_value = 10.
        self.VNA.set_marker_X(marker_index=1, frequency= test_value)
        self.assertEqual(self.VNA.get_marker_X, test_value)

    def set_sweep_points(self):
        test_value = 1001
        self.VNA.set_sweep_points(points=test_value)
        self.assertEqual(self.VNA.get_sweep_points, test_value)

    def set_sweep_range(self):
        test_value = (5, 15)
        self.VNA.set_sweep_points(*test_value)
        self.assertEqual(self.VNA.get_sweep_points, test_value)
        
if __name__=="__main__":
    unittest.main()
