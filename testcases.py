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

    def test_binary_exists(self):
        sftp = self.ssh.open_sftp()
        filename = "/usr/sbin/apache2"
        try:
            sftp.stat(filename)
        except FileNotFoundError:
            self.fail("File does not exist: %s" % (filename))

    def test_service_is_running(self):
        stdin, stdout, stderr = self.ssh.exec_command("systemctl is-active apache2")
        result = stdout.read().decode("utf-8").strip()
        self.assertEqual(result, "active")

    def test_service_is_running_after_reboot(self):
        self.reset_vm()
        stdin, stdout, stderr = self.ssh.exec_command("systemctl is-active apache2")
        result = stdout.read().decode("utf-8").strip()
        self.assertEqual(result, "active")


if __name__ == "__main__":
    testbench.main()
