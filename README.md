# TestBench #

TestBench is a micro-framework for integration testing with VirtualBox and SSH.
It is built on top of Pythons well-known unittest module and the popular
Paramiko SSH library.

# Installation #

```bash
pip3 install testbench
```

# Get Started #

## Create a VM in VirtualBox ##

Create a Linux VM in VirtualBox and install all the basic software you want to
have available in all of your tests.

## Configure SSH ##

Create directory where you want to put your tests in (e.g. integration_tests).
Now go to this directory and create a file name ssh_config.json with the
following contents:

```json
{
    "username": "user",
    "password": "pass",
    "port": "22",
    "tunneled_ports": [
    ]
}
```

Replace the credentials with those of your VM.

If you prefer to use key based authentication your config file will look like
this:

```json
{
    "username": "user",
    "keyfile": "/path/to/ssh/key",
    "port": "22",
    "tunneled_ports": [
    ]
}
```

## Write Your First Test ##

Copy the following code and save it to a file named "tests.py":

```python
#!/usr/bin/env python3

import testbench

class TestVirtualMachine(testbench.TestCase):

    def test_apache(self):
        # check if the Apache binary exists on the VM
        sftp = self.ssh.open_sftp()
        filename = "/usr/sbin/apache2"
        try:
            sftp.stat(filename)
        except FileNotFoundError:
            self.fail("File does not exist: %s" % (filename))

        # check if Apache is running on the VM
        stdin, stdout, stderr = self.ssh.exec_command("systemctl is-active apache2")
        result = stdout.read().decode("utf-8").strip()
        self.assertEqual(result, "active")


if __name__ == "__main__":
    testbench.main()
```

Now make the file executable with

```bash
chmod a+x tests.py
```

## Run Your Test ##

You can now run your test with the following command (replace "My VM" with the
name of your VM in VirtualBox and 1.2.3.4 with the IP of your VM):

```bash
./tests.py "My VM" 1.2.3.4
```

TestBench will now check if your VM already has a snapshot named
"testbench_base_snapshot". If no such snapshot exists TestBench will create it
from the current state of the VM.

TestBench will revert your machine to this base snapshot before the run of each
of your tests. It will also make sure that each test has a working SSH
connection to your VM.

![Base Snapshot in VirtualBox](/pics/vbox-snapshots.png)

## License ##

TestBench is licensed under the MIT license.

## Contact ##

Andreas Heck <<aheck@gmx.de>>
