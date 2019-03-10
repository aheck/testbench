#!/usr/bin/env python3

import sys
import os.path
import testbench
import unittest

import virtualbox
from virtualbox.library import MachineState
from virtualbox.library import LockType
from virtualbox.library import SessionState

class TestVirtualMachine(testbench.TestCase):

    def test_something(self):
        print(self.TESTBENCH_DATA)
        stdin, stdout, stderr = self.ssh.exec_command('touch unittest_was_here.txt')

    def test_more(self):
        pass


if __name__ == '__main__':
    testbench.main()
