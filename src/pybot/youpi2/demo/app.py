# -*- coding: utf-8 -*-

import pkgutil
import json

from pybot.youpi2.app import YoupiApplication

from pybot.youpi2.demo.stmts import STATEMENTS
from pybot.youpi2.demo.__version__ import version

__author__ = 'Eric Pascual'


class AutomaticDemoApp(YoupiApplication):
    NAME = 'demo-auto'
    TITLE = "Standalone demo"
    VERSION = version

    STATE_IDLE, STATE_LOADED, STATE_EXECUTING = range(3)

    sequence = []
    steps_count = 0
    step_num = 0
    current_step = None
    state = STATE_IDLE

    def add_custom_arguments(self, parser):
        parser.add_argument('--sequence-name', default="test")

    def setup(self, sequence_name="test", **kwargs):
        src = json.loads(pkgutil.get_data('pybot.youpi2.demo', 'data/%s.json' % sequence_name))
        for keyw, args in src:
            try:
                step_class = STATEMENTS[keyw]
            except KeyError:
                raise ValueError('invalid keyword: %s' % keyw)
            else:
                self.sequence.append(step_class(self.arm, self.logger, **args))

        self.steps_count = len(self.sequence)
        self.logger.info("sequence: %s", self.sequence)

    def loop(self):
        if self.state == self.STATE_IDLE:
            self.current_step = self.sequence[self.step_num]
            self.state = self.STATE_LOADED

        elif self.state == self.STATE_LOADED:
            self.pnl.write_at(
                ('step #%d > %s' % (self.step_num, self.current_step.KEYWORD)).ljust(self.pnl.width),
                3
            )
            self.pnl.write_at(
                self.current_step.args_repr.replace(' ', '').ljust(self.pnl.width)[:self.pnl.width],
                4
            )
            self.logger.info(
                'executing step #%d : %s(%s)',
                self.step_num, self.current_step.KEYWORD, self.current_step.args_repr
            )
            self.current_step.execute()
            self.state = self.STATE_EXECUTING

        elif self.state == self.STATE_EXECUTING:
            if self.current_step.is_done():
                if self.steps_count == 1:
                    return True

                self.step_num = (self.step_num + 1) % len(self.sequence)
                self.state = self.STATE_IDLE

        else:
            raise RuntimeError('invalid state (%s)' % self.state)

    def teardown(self, exit_code):
        self.pnl.center_text_at('terminating', 3)
        self.arm.soft_hi_Z()
        self.logger.info('arm set in Hi-Z')


def main():
    AutomaticDemoApp().main()
