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

    def __str__(self):
        return self.KEYWORD + ' ' + self.args_repr


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
class GotoPoseStmt(SequenceStatement):
    KEYWORD = 'POSE'

    def __init__(self, arm, logger, angles=None):
        super(GotoPoseStmt, self).__init__(arm, logger)
        self.angles = {YoupiArm.MOTOR_NAMES.index(j): a for j, a in angles.iteritems()}
        self.args_repr = 'angles=%s' % self.angles

    def execute(self):
        self.arm.goto(self.angles, False)

    def is_done(self):
        return not self.arm.is_moving()


@register
class DelayStmt(SequenceStatement):
    KEYWORD = 'DELAY'

    def __init__(self, arm, logger, seconds=1):
        super(DelayStmt, self).__init__(arm, logger)

        try:
            self.seconds = int(seconds)
        except ValueError:
            self.logger.error('invalid seconds value (%(arg)s) for %(keyw)s', {'arg': seconds, 'keyw': self.KEYWORD})
            raise

        self.limit = None
        self.args_repr = 'seconds=%d' % self.seconds

    def execute(self):
        self.limit = time.time() + self.seconds

    def is_done(self):
        return time.time() >= self.limit


@register
class GripperStmt(SequenceStatement):
    KEYWORD = 'GRIPPER'

    def __init__(self, arm, logger, action):
        super(GripperStmt, self).__init__(arm, logger)

        try:
            action = action.lower()
            if action not in ('open', 'close'):
                raise ValueError()

            self.open = action == 'open'
        except ValueError:
            self.logger.error('invalid action value (%s) for GRIPPER', action)
            raise

        self.args_repr = 'action=%s' % action

    def execute(self):
        self.arm.open_gripper(True) if self.open else self.arm.close_gripper(True)

    def is_done(self):
        return not self.arm.is_moving()


@register
class HomeStmt(SequenceStatement):
    KEYWORD = 'HOME'

    def __init__(self, arm, logger, joints):
        super(HomeStmt, self).__init__(arm, logger)

        if isinstance(joints, (list, tuple)):
            self.joints = []
            for j in joints:
                name = j.lower()
                if name not in YoupiArm.MOTOR_NAMES:
                    raise ValueError("invalid joint name (%s)" % j)
                if name != YoupiArm.GRIPPER_MOTOR_NAME:
                    self.joints.append(name)

        elif joints == '*':
            self.joints = YoupiArm.JOINT_MOTOR_NAMES

        else:
            raise ValueError("invalid joints list (%s)" % joints)

    def execute(self):
        self.arm.go_home(self.joints, True)

    def is_done(self):
        return not self.arm.is_moving()
