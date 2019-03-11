import os
import sys
import time

import virtualbox
from virtualbox.library import MachineState
from virtualbox.library import LockType
from virtualbox.library import SessionState

BASE_SNAPSHOT_NAME = 'testbench_base_snapshot'

def iterate_all_snapshots(vm):
    if vm.snapshot_count <= 0:
        return

    root = vm.find_snapshot('')

    stack = [[root]]
    cur = root

    while len(stack) > 0:
        frame = stack.pop()
        frame.reverse()
        for cur in frame:
            yield cur
            if (cur.children):
                stack.append(cur.children)


def find_snapshot(vm, name):
    for snapshot in iterate_all_snapshots(vm):
        if snapshot.name == name:
            return snapshot

    return None


def create_base_snapshot_if_not_exists(vm):
    if not find_snapshot(vm, BASE_SNAPSHOT_NAME):
        print("Snapshot %s doesn't exist. Creating..." % (BASE_SNAPSHOT_NAME))
        (progress, p_id) = vm.take_snapshot(BASE_SNAPSHOT_NAME,
                'Starting point for all testbench test cases', False)

        while not progress.completed:
            time.sleep(0.5)
            print("Progress: %d" % (progress.percent))


def wait_for_vm_lock_release(vm):
    while vm.session_state != SessionState.unlocked:
        print("Waiting for VM lock to be released...")
        time.sleep(0.5)


def restore_machine(vm_name, vm, session):
    print("Restoring machine to snapshot %s..." % (BASE_SNAPSHOT_NAME))
    print("State: %s" % (vm.state))
    if vm.state in [MachineState.running, MachineState.paused, MachineState.stuck]:
        progress = session.console.power_down()
        progress.wait_for_completion(10000)

    progress = vm.restore_snapshot(vm.find_snapshot(BASE_SNAPSHOT_NAME))
    progress.wait_for_completion(10000)

    session.unlock_machine()

    vbox = virtualbox.VirtualBox()
    vm = vbox.find_machine(vm_name)
    session = virtualbox.Session()

    wait_for_vm_lock_release(vm)

    progress = vm.launch_vm_process(session, 'gui', '')
    progress.wait_for_completion(10000)

    return session
