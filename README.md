# TestBench #

TestBench is a micro-framework for integration testing with VirtualBox and SSH.

It is built on top of Pythons well-known unittest module and it uses the
popular Paramiko SSH library to give tests access to the VM where the software
to be tested runs on.

# Installation #

```bash
pip3 install testbench
```

# Get Started #

## Create a VM in VirtualBox ##

Create a Linux VM in VirtualBox and install all the basic software you want to
have available in all of your tests.

Your VM must have a virtual network interface that is bridged to the network
of your host machine and there must be a SSH server up and running. We will
later use this interface to connect to your VM via SSH so your tests can
instrument the VM.

## Configure SSH ##

Create a directory where you want to put your tests in (e.g. integration_tests).
Now go to this directory and create a file named ssh_config.json with the
following contents:

```json
{
    "username": "user",
    "password": "password",
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

# Advanced Features #

## Port Forwarding ##

If you want to test a webservice that is served by an Apache webserver running
on your testing VM you can just access it directly because by default
Apache listens on all addresses (IPv4 address 0.0.0.0).

But what if you want to connect to a service on a test VM which only listens
for connections coming from the local machine (IPv4 address 127.0.0.1)?

MySQL is one such service. For security reasons it only accepts connections from
127.0.0.1 by default. If you check for open ports on a testing VM with MySQL
and Apache installed you might get something like this:

```bash
~$ netstat -lnt
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
```

You can access Apache from your local machine but not MySQL. Of course you could
reconfigure MySQL to listen for incoming connections from external sources.

But for security reasons it is a good idea to only allow connections that are
strictly necessary and when testing you want to stay as close to your
production deployment as possible.

To solve such problems TestBench supports port forwardings. To forward the MySQL
port on your testing VM to your local machine just add an entry for MySQL to
your ssh_config.json like in this example:

```json
{
    "username": "user",
    "password": "password",
    "port": "22",
    "tunneled_ports": [
        {"name": "mysql", "port": 3306}
    ]
}
```

TestBench will now create an SSH tunnel from a random port on your local machine
to MySQL on port 3306 on your testing VM whenever it creates an SSH connection 
to the VM.

In your test cases you can fetch the random port number from the dictionary
self.port_forwards and use it to connect to MySQL on the testing VM:

```python
#!/usr/bin/env python3

import testbench
import mysql.connector

class TestVirtualMachine(testbench.TestCase):

    def test_mysql(self):
        mysql_port = str(self.port_forwards['mysql']['local_port'])
        conn = mysql.connector.connect(user='user', password='password',
                              host='127.0.0.1', port=mysql_port
                              database='testdb')
        conn.close()


if __name__ == "__main__":
    testbench.main()
```

# License #

TestBench is licensed under the MIT license.

# Contact #

Andreas Heck <<aheck@gmx.de>>
