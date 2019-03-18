#!/usr/bin/env python3

import testbench
import socket

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

    def test_port_forwarded_services(self):
        # By default MySQL listens only on loopback addresses therefore we need
        # to use an SSH tunnel to access it from our testing machine.
        mysql_port = self.port_forwards['mysql']['local_port']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', mysql_port))

        if result == 0:
            try:
                data = sock.recv(1024)
                data = data.decode("unicode_escape")

                # the MySQL binary protocol greets us with message containing the
                # string "mysql_native_password"
                self.assertTrue("mysql_native_password" in data)
            finally:
                sock.close()
        else:
            self.assertFail("MySQL port forwarding on local port %s does not work" % (mysql_port))

        # Of course Apache listens on all addresses so we could reach it directly
        # just by connecting to the VM IP. But we want to show that testbench can
        # tunnel more than one port so here we go:
        apache_port = self.port_forwards['apache']['local_port']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', apache_port))

        if result == 0:
            try:
                request = "HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n"
                sock.send(request.encode("ascii"))
                data = sock.recv(1024)
                reply = data.decode("utf-8")
                self.assertTrue("HTTP/1.1 200 OK" in reply)
            finally:
                sock.close()
            pass
        else:
            self.assertFail("Apache port forwarding on local port %s does not work" % (apache_port))


if __name__ == "__main__":
    testbench.main()
