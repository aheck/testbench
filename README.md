# TestBench #

TestBench is a micro-framework for integration testing with VirtualBox and SSH.
It is built on top of Pythons well-known unittest module and the popular
Paramiko SSH library.

# How does it work? #

1. Create a VM in VirtualBox and install all the software you want to have
   available in all of your tests.
2. Write a test file which looks like a test written for Pythons unittest framework
   except for the minor difference that all test classes inherit from
   testbench.TestCase instead of unittest.TestCase. You can also access the
   machine by using the Paramiko SSH client available in self.ssh
3. Create a ssh_config.json from the provided ssh_config.json.tmpl template
   file.
4. Run your tests.

TestBench will now check if your virtual machine has a snapshot with the name
testbench_base_snapshot. If no such snapshot exists TestBench will create it
from the current state of your machine.

Then it will restore your machine back to this state before each test is run
and it will also create a new SSH connection for each test run. So each of
your tests will run on a VM with a completely clean state.
