import os
import unittest

import sys

from parameterized import parameterized

from utils.emulator_launcher import BeckhoffEmulatorLauncher
from utils.test_modes import TestModes
from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir, EPICS_TOP
from utils.testing import skip_if_recsim, get_running_lewis_and_ioc, parameterized_list
from time import sleep

# Device prefix
DEVICE_PREFIX = "TC_01"
EMULATOR_NAME = "PLC_solution"

BECKHOFF_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("TC"),
        "macros": {
            "NUM_AXES": "9",
            "IP_AD":"127.0.0.1",
            "AMS_ID":"127.0.0.1.1.1",
			"PLC_VERSION": "1",
            "MTRCTRL": "1",
            "TWINCATCONFIG": os.path.join(BECKHOFF_ROOT, EMULATOR_NAME, "solution", "tc_project_app").replace(os.path.sep, "/")
        },
        "emulator": EMULATOR_NAME,
        "emulator_launcher_class": BeckhoffEmulatorLauncher,
        "beckhoff_root": BECKHOFF_ROOT,
        "custom_prefix": "MOT",
        "pv_for_existence": "MTR0101",
    },
]


TEST_MODES = [TestModes.DEVSIM, TestModes.NOSIM]

MOTOR_SP_BASE = "MOT:MTR010{}"
MOTOR_RBV_BASE = MOTOR_SP_BASE + ".RBV"
MOTOR_ON_STATUS = MOTOR_SP_BASE + "_ON_STATUS"
MOTOR_ON_CMD = MOTOR_SP_BASE + "_ON_CMD"

MOTOR_MOVING_BASE = MOTOR_SP_BASE + ".MOVN"
MOTOR_DONE_BASE = MOTOR_SP_BASE + ".DMOV"
MOTOR_STOP_BASE = MOTOR_SP_BASE + ".STOP"
MOTOR_VELO_BASE = MOTOR_SP_BASE + ".VELO"
MOTOR_DIR_BASE = MOTOR_SP_BASE + ".DIR"

MOTOR_SP = MOTOR_SP_BASE.format(1)
MOTOR_RBV = MOTOR_RBV_BASE.format(1)
MOTOR_DONE = MOTOR_SP + ".DMOV"
MOTOR_DIR = MOTOR_SP + ".TDIR"
MOTOR_STOP = MOTOR_SP + ".STOP"
MOTOR_JOGF = MOTOR_SP + ".JOGF"
MOTOR_JOGR = MOTOR_SP + ".JOGR"
MOTOR_VELO = MOTOR_SP + ".VELO"
MOTOR_RTRY = MOTOR_SP + ".RTRY"

MOTOR_2_SP = MOTOR_SP_BASE.format(2)
MOTOR_2_RBV = MOTOR_RBV_BASE.format(2)

ENABLE = DEVICE_PREFIX + ":ASTAXES_{}:STCONTROL-BENABLE"
ENABLED = DEVICE_PREFIX + ":ASTAXES_{}:STSTATUS-BENABLED"
LIMIT_FWD = DEVICE_PREFIX + ":ASTAXES_{}:STINPUTS-BLIMITFWD"
LIMIT_BWD = DEVICE_PREFIX + ":ASTAXES_{}:STINPUTS-BLIMITBWD"
RESET = DEVICE_PREFIX + ":ASTAXES_{}:STCONTROL-BRESET"

class TcIocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emulator, cls._ioc = get_running_lewis_and_ioc(EMULATOR_NAME, DEVICE_PREFIX)

        cls.ca = ChannelAccess(device_prefix=None, default_wait_time=0.0)

    def setUp(self):
        # Only setup for axes 1 and 9 - they are the only ones tested and therefore need to be set.
        for i in [1, 9]:
            self.ca.set_pv_value(RESET.format(i), 1)
            self.ca.set_pv_value(ENABLE.format(i), 1)
            self.ca.set_pv_value(MOTOR_DIR_BASE.format(i), 0)
            self.ca.set_pv_value(LIMIT_FWD.format(i), 1)
            self.ca.set_pv_value(LIMIT_BWD.format(i), 1)
            self.ca.set_pv_value(MOTOR_STOP_BASE.format(i), 1)
            self.ca.set_pv_value(MOTOR_VELO_BASE.format(i), 1)
            self.ca.set_pv_value(MOTOR_SP_BASE.format(i), 0)
            self.ca.assert_that_pv_is(MOTOR_DONE_BASE.format(i), 1, timeout=10)

    def check_moving(self, expected_moving, axis_num=1):
        sleep(0.2)  # Moving has a slight delay so allow for 200ms to update
        self.ca.assert_that_pv_is(MOTOR_MOVING_BASE.format(axis_num), int(expected_moving), timeout=1)
        self.ca.assert_that_pv_is(MOTOR_DONE_BASE.format(axis_num), int(not expected_moving), timeout=1)

    @parameterized.expand(
        parameterized_list([3.5, 6, -10])
    )
    def test_WHEN_moving_to_position_THEN_status_is_moving_and_gets_to_position(self, _, target):
        self.ca.set_pv_value(MOTOR_SP, target)
        self.check_moving(True)
        self.ca.assert_that_pv_is(MOTOR_RBV, target, timeout=20)

    def test_WHEN_moving_forward_THEN_motor_record_in_positive_direction(self):
        self.ca.set_pv_value(MOTOR_SP, 2)
        self.ca.assert_that_pv_is(MOTOR_DIR, 1)

    def test_WHEN_moving_backwards_THEN_motor_record_in_backwards_direction(self):
        self.ca.set_pv_value(MOTOR_SP, -2)
        self.ca.assert_that_pv_is(MOTOR_DIR, 0)
        
    def test_WHEN_commanded_dir_is_changed_at_motor_record_THEN_motor_record_flips_limits(self):
        # Set dir on motor record
        self.ca.set_pv_value(MOTOR_DIR_BASE.format(1), 1)
        # Enable fwd limit switch
        self.ca.set_pv_value(LIMIT_FWD.format(1), 0)
        # Assert that lower (opposite) limit switch is shown
        self.ca.assert_that_pv_is(MOTOR_SP + ".LLS", 1)
        
    def test_WHEN_commanded_dir_is_changed_at_motor_record_THEN_motor_record_flips_reported_direction(self):
        # Set dir on motor record then send a positive user SP
        self.ca.set_pv_value(MOTOR_DIR_BASE.format(1), 1)
        self.ca.set_pv_value(MOTOR_SP, 2)
        # Assert that we are driving negatively
        self.ca.assert_that_pv_is(MOTOR_DIR, 1)

    def test_WHEN_moving_THEN_can_stop_motion(self):
        self.ca.set_pv_value(MOTOR_SP, 100)
        self.check_moving(True)
        self.ca.set_pv_value(MOTOR_STOP, 1)
        self.check_moving(False)
        self.ca.assert_that_pv_is_not_number(MOTOR_RBV, 100, 10)

    @parameterized.expand(
        parameterized_list([(MOTOR_JOGR, 0), (MOTOR_JOGF, 1)])
    )
    def test_WHEN_jogging_THEN_can_stop_motion(self, _, pv, direction):
        self.ca.set_pv_value(pv, 1)
        self.ca.assert_that_pv_is(MOTOR_DIR, direction)
        self.check_moving(True)
        self.ca.set_pv_value(MOTOR_STOP, 1)
        self.check_moving(False)

    @parameterized.expand(
        parameterized_list([(".HLS", LIMIT_FWD.format(1)), (".LLS", LIMIT_BWD.format(1))])
    )
    def test_WHEN_limits_hit_THEN_motor_reports_limits(self, _, motor_pv_suffix, pv_to_set):
        self.ca.set_pv_value(pv_to_set, 0)
        self.ca.assert_that_pv_is(MOTOR_SP + motor_pv_suffix, 1)
    
    def test_WHEN_axis_set_up_THEN_retries_are_not_allowed(self):
        self.ca.assert_that_pv_is(MOTOR_RTRY, 0)

    @parameterized.expand(
        parameterized_list([1, 0])
    )
    def test_WHEN_enabled_set_on_plc_THEN_motor_status_on_is_set_correctly(self, _, desired_state):
        axis_num = 1
        self.ca.set_pv_value(ENABLE.format(axis_num), not desired_state)
        self.ca.assert_that_pv_is(MOTOR_ON_STATUS.format(axis_num), not desired_state)

        self.ca.set_pv_value(ENABLE.format(axis_num), desired_state)
        self.ca.assert_that_pv_is(MOTOR_ON_STATUS.format(axis_num), desired_state)
    
    @parameterized.expand(
        parameterized_list([1, 0])
    )
    def test_WHEN_enabled_set_via_mtr_rec_THEN_PLC_is_updated(self, _, desired_state):
        axis_num = 1
        self.ca.set_pv_value(MOTOR_ON_CMD.format(axis_num), not desired_state)
        self.ca.assert_that_pv_is(MOTOR_ON_STATUS.format(axis_num), not desired_state)
        self.ca.assert_that_pv_is(ENABLED.format(axis_num), not desired_state)

        self.ca.set_pv_value(MOTOR_ON_CMD.format(axis_num), desired_state)
        self.ca.assert_that_pv_is(MOTOR_ON_STATUS.format(axis_num), desired_state)
        self.ca.assert_that_pv_is(ENABLED.format(axis_num), desired_state)

        
    @parameterized.expand(
        parameterized_list([0.5, -0.5])
    )
    def test_WHEN_axis_9_changed_THEN_original_and_aliased_motor_record_updates(self, _, target):
        self.ca.set_pv_value(MOTOR_SP_BASE.format(9), target)
        self.ca.assert_that_pv_is("MOT:MTR0201:SP", target)
        # make sure motor 1 has not moved
        self.ca.assert_that_pv_is_number(MOTOR_RBV, 0)
