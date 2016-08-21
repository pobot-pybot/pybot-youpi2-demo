# -*- coding: utf-8 -*-

import argparse
import time
import datetime

from pybot.youpi2.ctlpanel import ControlPanel
from pybot.youpi2.ctlpanel.devices.fs import FileSystemDevice

__author__ = 'Eric Pascual'


class DemoAuto(object):
    @staticmethod
    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('--pnldev', default="/mnt/lcdfs")

        args = parser.parse_args()

        DemoAuto(pnldev=args.pnldev).run()

    def __init__(self, pnldev="/mnt/lcdfs"):
        self.pnl = ControlPanel(FileSystemDevice(pnldev))

    def run(self):
        self.pnl.clear()
        self.pnl.center_text_at("Automatic demo", line=1)

        while True:
            self.pnl.center_text_at(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), line=3)

            time.sleep(1)

