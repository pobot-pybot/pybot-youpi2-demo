# -*- coding: utf-8 -*-

import time

from pybot.youpi2.model import YoupiArm

__author__ = 'Eric Pascual'


class SequenceStatement(object):
    args_repr = ''

    def __init__(self, arm, logger, **kwargs):
        self.arm = arm
        self.logger = logger

    def execute(self):
        raise NotImplementedError()

    def is_done(self):
        raise NotImplementedError()


STATEMENTS = {}


def register(cls):
    try:
        STATEMENTS[cls.KEYWORD] = cls
    except AttributeError:
        pass
    return cls


@register
class MoveStmt(SequenceStatement):
    KEYWORD = 'MOVE'

    def __init__(self, arm, logger, angles=None):
        super(MoveStmt, self).__init__(arm, logger)
        self.angles = {YoupiArm.MOTOR_NAMES.index(j): a for j, a in angles.iteritems()}
        self.args_repr = 'angles=%s' % self.angles

    def execute(self):
        self.arm.move(self.angles, False)

    def is_done(self):
        return not self.arm.is_moving()


@register
class GotoStmt(SequenceStatement):
    KEYWORD = 'GOTO'

    def __init__(self, arm, logger, pose=None):
        super(GotoStmt, self).__init__(arm, logger)
        self.pose = {YoupiArm.MOTOR_NAMES.index(j): a for j, a in pose.iteritems()}
        self.args_repr = 'pose=%s' % self.pose

    def execute(self):
        self.arm.goto(self.pose, False)

    def is_done(self):
        return not self.arm.is_moving()


@register
class PauseStmt(SequenceStatement):
    KEYWORD = 'PAUSE'

    def __init__(self, arm, logger, delay=1):
        super(PauseStmt, self).__init__(arm, logger)

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
