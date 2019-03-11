import json
import paramiko

def read_ssh_config(filename):
    with open(filename, "r") as f: data=f.read()
    json_data = json.loads(data)
    return json_data

def connect_ssh(hostname, ssh_config):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname,
            username=ssh_config['username'],
            password=ssh_config['password'],
            port=ssh_config['port'],
            timeout=120)

    return ssh
