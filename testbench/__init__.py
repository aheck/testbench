from testbench.virtualbox import *
from testbench.ssh import *

import unittest

import socket
import time

import virtualbox
from virtualbox.library import LockType

class TestCase(unittest.TestCase):

    def setUp(self):
        vmname = self.TESTBENCH_DATA['vmname']
        vm = self.TESTBENCH_VM

        session = virtualbox.Session()
        vm.lock_machine(session, LockType.shared)
        vm = session.machine

        create_base_snapshot_if_not_exists(vm)
        self.TESTBENCH_SESSION = restore_machine(vmname, vm, session)

        self._connect_ssh()

    def tearDown(self):
        self._disconnect_ssh()

    def reset_vm(self):
        self._disconnect_ssh()

        self.TESTBENCH_SESSION.console.reset()

        hostname = self.TESTBENCH_DATA['hostname']

        self._connect_ssh(wait=True)

    def _connect_ssh(self, wait=False):
        hostname = self.TESTBENCH_DATA['hostname']
        ssh_config = self.TESTBENCH_DATA['ssh_config']

        # wait until the SSH port on the VM is ready
        if wait:
            i = 0
            while True:
                i += 1
                if i > 30:
                    raise Exception("SSH port %d didn't come up",
                            ssh_config['port'])

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((hostname, int(ssh_config['port'])))
                if result != 0:
                    sock.close()
                    time.sleep(10)
                else:
                    sock.close()
                    break

        (self.ssh, self.port_forwards, self._servers) = connect_ssh(hostname, ssh_config)

    def _disconnect_ssh(self):
        # terminate the port forwardings
        for server in self._servers:
            server.server_close()

        self.ssh.close()


def usage():
    prgname = os.path.basename(__file__)
    print("Usage: %s VMNAME HOSTNAME [SINGLETEST]" %(prgname))
    print()
    print("Example: %s my_vbox_vm 192.168.0.120" % (prgname))
    print()
    print("Arguments:")
    print()
    print("  VMNAME:     The name of your VM in VirtualBox")
    print("  HOSTNAME:   The Hostname or IP address of your VM")
    print("  SINGLETEST: Run only this test. Classname AND testname.")
    print("              E.g.: TestClass.my_test")
    sys.exit(2)


def main(ssh_config_filename="ssh_config.json"):
    argvlen = len(sys.argv)
    if argvlen < 3 or argvlen > 4:
        usage()

    vmname = sys.argv[1]
    hostname = sys.argv[2]
    singletest = None
    if argvlen == 4:
        singletest = sys.argv[3]

    # Remove the command line args so unittest.main() does not try
    # to interpret them
    for _ in range(argvlen - 1):
        sys.argv.pop()

    try:
        vbox = virtualbox.VirtualBox()
        vm = vbox.find_machine(vmname)
    except Exception:
        print("Couldn't find VirtualBox VM: %s" % (vmname), file=sys.STDERR)
        sys.exit(1)

    ssh_config = read_ssh_config(ssh_config_filename)
    testbench_data = {'vmname': vmname, 'hostname': hostname,
            'ssh_config': ssh_config}

    for test_class in TestCase.__subclasses__():
        test_class.TESTBENCH_DATA = testbench_data
        test_class.TESTBENCH_VM = vm

        # we need to delete to class object or else unittest executes each
        # testase class twice
        del test_class

    sys.argv.append("-v")
    if singletest:
        sys.argv.append(singletest)
    unittest.main()
