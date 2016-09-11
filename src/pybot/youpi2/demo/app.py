# -*- coding: utf-8 -*-

import pkgutil
import json

from pybot.youpi2.app import YoupiApplication

__author__ = 'Eric Pascual'


class AutomaticDemoApp(YoupiApplication):
    NAME = 'demo-auto'
    TITLE = "Standalone demo"

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
        if not self.arm.moving:
            self.pnl.center_text_at('current step: %d' % self.step_num, 3)
            pose = self.sequence[self.step_num]
            self.arm.goto(pose, wait=False)

            self.step_num = (self.step_num + 1) % len(self.sequence)

    def teardown(self, exit_code):
        self.pnl.center_text_at('terminating', 3)
        if self.arm.moving:
            self.arm.stop()


def main():
    AutomaticDemoApp().main()
