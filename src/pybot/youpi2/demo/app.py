# -*- coding: utf-8 -*-

import pkgutil
import json

from pybot.youpi2.app import YoupiApplication
from pybot.youpi2.model import YoupiArm

from .__version__ import version

__author__ = 'Eric Pascual'


class AutomaticDemoApp(YoupiApplication):
    NAME = 'demo-auto'
    TITLE = "Standalone demo"
    VERSION = version

    sequence = None
    step_num = 0

    def add_custom_arguments(self, parser):
        parser.add_argument('--sequence-name', default="test")

    def setup(self, sequence_name="test", **kwargs):
        self.sequence = json.loads(pkgutil.get_data('pybot.youpi2.demo', 'data/%s.json' % sequence_name))
        self.logger.info("sequence: %s", self.sequence)

    def loop(self):
        # if the arm is not moving, advance to the next sequence step,
        # looping when reaching its end
        if not self.arm.is_moving():
            self.pnl.center_text_at('current step: %d' % self.step_num, 3)
            pose = {YoupiArm.MOTOR_NAMES.index(j): a for j, a in self.sequence[self.step_num].iteritems()}
            self.arm.goto(pose, False)

            self.step_num = (self.step_num + 1) % len(self.sequence)

    def teardown(self, exit_code):
        self.pnl.center_text_at('terminating', 3)
        self.arm.soft_hi_Z()
        self.logger.info('arm set in Hi-Z')


def main():
    AutomaticDemoApp().main()
