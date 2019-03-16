import json
import paramiko
import os
import random
import select
import socket
import threading

import socketserver as SocketServer

CONNECT_TIMEOUT = 360
BANNER_TIMEOUT = 120
AUTH_TIMEOUT = 120

def generate_random_port():
    return random.randint(1025, 65535)


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class ForwardHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        host = '127.0.0.1'
        try:
            channel = self.ssh_transport.open_channel("direct-tcpip",
                (host, self.target_port), self.request.getpeername())
        except Exception as e:
            print("Failed to create channel to %s:%d: %r"
                % (self.target_host, self.target_port, e))
            return

        if channel is None:
            print("Failed to create tunnel to: %s:%d"
                % (self.target_host, self.target_port))
            return

        (ip, host) = self.request.getpeername()
        print("Tunnel connected from %s:%d to %s:%d" % (ip, host,
            self.target_host, self.target_port))

        blocksize = 1024
        while True:
            r, w, _ = select.select([self.request, channel], [], [])

            if self.request in r:
                data = self.request.recv(blocksize)
                if len(data) == 0:
                    break
                channel.send(data)

            if channel in r:
                data = channel.recv(blocksize)
                if len(data) == 0:
                    break
                self.request.send(data)

        (ip, port) = self.request.getpeername()
        channel.close()
        self.request.close()
        print("Tunnel closed from %s:%d to %s:%d"
                % (ip, port, self.target_host, self.target_port))


def forward_local_port(local_port, remote_host, remote_port, transport):
    class HandlerWrapper(ForwardHandler):
        target_host = remote_host
        target_port = remote_port
        ssh_transport = transport

    server =  ForwardServer(("", local_port), HandlerWrapper)
    threading.Thread(daemon=True, target=server.serve_forever).start()

    return server


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
                timeout=CONNECT_TIMEOUT,
                banner_timeout=BANNER_TIMEOUT,
                auth_timeout=AUTH_TIMEOUT)
    else:
        ssh.connect(hostname,
                username=ssh_config['username'],
                password=ssh_config['password'],
                port=port,
                timeout=CONNECT_TIMEOUT,
                banner_timeout=BANNER_TIMEOUT,
                auth_timeout=AUTH_TIMEOUT)

    # setup all port forwardings
    port_forwards = {}
    servers = []
    for entry in ssh_config['tunneled_ports']:
        local_port = generate_random_port()
        server = forward_local_port(local_port, hostname,
                entry['port'], ssh.get_transport())
        servers.append(server)

        port_forwards[entry['name']] = {'local_port': local_port}

    return ssh, port_forwards, servers
