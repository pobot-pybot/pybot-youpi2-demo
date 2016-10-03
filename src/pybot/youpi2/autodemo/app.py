# -*- coding: utf-8 -*-

import pkgutil
import json
import os

from pybot.youpi2.app import YoupiApplication

from stmts import STATEMENTS
from __version__ import version

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
        parser.add_argument('--sequence-name', default="default")

    def setup(self, sequence_name="test", **kwargs):
        res_local_path = 'data/%s.json' % sequence_name
        res_path = os.path.join(os.path.dirname(__file__), res_local_path)
        self.logger.info("loading sequence from: %s", res_path)
        self.logger.info("- source file:")
        pkg_name = '.'.join(__name__.split('.')[:-1])
        src = pkgutil.get_data(pkg_name, res_local_path)
        for line in src.splitlines():
            self.logger.info("  " + line)
        try:
            js = json.loads(src)
        except ValueError as e:
            raise ValueError('invalid source file: %s' % e)

        self.logger.info("- compiled statements:")
        for keyw, args in js:
            try:
                step_class = STATEMENTS[keyw]
            except KeyError:
                raise ValueError('invalid keyword: %s' % keyw)
            else:
                stmt = step_class(self.arm, self.logger, **args)
                self.sequence.append(stmt)
                self.logger.info("  " + str(stmt))

        self.steps_count = len(self.sequence)
        self.logger.info("complete (%s statements)", self.steps_count)

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


def main():
    AutomaticDemoApp().main()
