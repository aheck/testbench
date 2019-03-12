import json
import paramiko

CONNECT_TIMEOUT = 360

def read_ssh_config(filename):
    with open(filename, "r") as f: data=f.read()
    json_data = json.loads(data)
    return json_data

def connect_ssh(hostname, ssh_config):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    port = 22
    if 'port' in ssh_config:
        port = ssh_config['port']

    if 'keyfile' in ssh_config:
        ssh.connect(hostname,
                username=ssh_config['username'],
                key_filename=ssh_config['keyfile'],
                port=port,
                timeout=CONNECT_TIMEOUT)
    else:
        ssh.connect(hostname,
                username=ssh_config['username'],
                password=ssh_config['password'],
                port=port,
                timeout=CONNECT_TIMEOUT)

    return ssh
