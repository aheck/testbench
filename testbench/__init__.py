from testbench.virtualbox import *
from testbench.ssh import *

import unittest

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
        self.ssh.close()

    def reset_vm(self):
        self.ssh.close()

        self.TESTBENCH_SESSION.console.reset()

        self._connect_ssh()

    def _connect_ssh(self):
        hostname = self.TESTBENCH_DATA['hostname']
        ssh_config = self.TESTBENCH_DATA['ssh_config']

        self.ssh = connect_ssh(hostname, ssh_config)

def usage():
    prgname = os.path.basename(__file__)
    print("Usage: %s VMNAME HOSTNAME" %(prgname))
    print()
    print("Example: %s my_vbox_vm 192.168.0.120" % (prgname))
    print()
    print("Arguments:")
    print()
    print("  VMNAME:   The name of your VM in VirtualBox")
    print("  HOSTNAME: The Hostname or IP address of your VM")
    sys.exit(2)

def main(ssh_config_filename="ssh_config.json"):
    if len(sys.argv) != 3:
        usage()

    vmname = sys.argv[1]
    hostname = sys.argv[2]

    # Remove the command line args so unittest.main() does not try
    # to interpret them
    sys.argv.pop()
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
    unittest.main()
