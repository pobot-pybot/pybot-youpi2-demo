# -*- coding: utf-8 -*-

import pkgutil
import json
import time

from pybot.youpi2.app import YoupiApplication
from pybot.youpi2.model import YoupiArm

from .__version__ import version

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
                step_class = _STATEMENTS[keyw]
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
                self.current_step.args_repr.ljust(self.pnl.width)[:self.pnl.width - 1],
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


class SequenceStep(object):
    args_repr = ''

    def __init__(self, arm, logger, **kwargs):
        self.arm = arm
        self.logger = logger

    def execute(self):
        raise NotImplementedError()

    def is_done(self):
        raise NotImplementedError()


_STATEMENTS = {}


def register(cls):
    try:
        _STATEMENTS[cls.KEYWORD] = cls
    except AttributeError:
        pass
    return cls


@register
class MoveStep(SequenceStep):
    KEYWORD = 'MOVE'

    def __init__(self, arm, logger, pose=None):
        super(MoveStep, self).__init__(arm, logger)
        self.pose = {YoupiArm.MOTOR_NAMES.index(j): a for j, a in pose.iteritems()}
        self.args_repr = 'pose=%s' % self.pose

    def execute(self):
        self.arm.goto(self.pose, False)

    def is_done(self):
        return not self.arm.is_moving()


@register
class PauseStep(SequenceStep):
    KEYWORD = 'PAUSE'

    def __init__(self, arm, logger, delay=1):
        super(PauseStep, self).__init__(arm, logger)

        try:
            self.delay = int(delay)
        except ValueError:
            self.logger.error('invalid delay value (%s) for PAUSE', delay)
            raise

        self.limit = None
        self.args_repr = 'delay=%d' % self.delay

    def execute(self):
        self.limit = time.time() + self.delay

    def is_done(self):
        return time.time() >= self.limit


def main():
    AutomaticDemoApp().main()
