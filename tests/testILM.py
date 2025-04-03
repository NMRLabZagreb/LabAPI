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
from pyILM import ILM

class TestAllGetterTypes(unittest.TestCase):
    """
    Test all getters types
    """
    def setUp(self):
        self.ips = ILM(device_present = True)

    # SIMPLE GETTERS (one value)
    def test_get_LHe_level(self):
        return_value = self.ips.get_LHe_level()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')

    def test_get_LN2_level(self):
        return_value = self.ips.get_LN2_level()
        self.assertIsInstance(return_value, float, f'Not a float but {type(return_value)}')