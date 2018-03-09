#!/usr/bin/env python3

import dialog

import os
import subprocess

d = dialog.Dialog()

class Bridge():
    def __init__(self, name, interfaces=[]):
        self.name = name
        self.interfaces = interfaces

    def create(self):
        cmd = [
                '/sbin/ip', 'link',
                'add', 'name', self.name,
                'type', 'bridge',
                ]
        subprocess.run(cmd)
        for interface in self.interfaces:
            cmd = [
                    '/sbin/ip', 'link',
                    'set', 'dev', interface,
                    'master', self.name
                    ]
            subprocess.run(cmd)

class VLAN():
    def __init__(self, name, master, vid):
        self.name = name
        self.master = master
        self.vid = vid

    def create(self):
        cmd = [
                '/sbin/ip', 'link',
                'add', 'link', self.master,
                'name', self.name,
                'type', 'vlan',
                'id', self.vid,
                ]
        subprocess.run(cmd)

def create_bridge():
    # We need to list the interfaces from the sysfs.
    choices = [(i, '', False) for i in os.listdir('/sys/class/net')]

    code, interfaces = d.checklist('Select the interfaces to add to the bridge.', choices=choices)

    if code == d.ESC or code == d.CANCEL:
        return

    code, name = d.inputbox('Please name your new bridge.')

    if code == d.ESC or code == d.CANCEL:
        return

    bridge = Bridge(name, interfaces)

    bridge.create()

def create_vlan():
    # We need to list the interfaces from the sysfs.
    choices = [(i, '') for i in os.listdir('/sys/class/net')]

    code, master = d.menu('Select the master interface to use.', choices=choices)

    if code == d.ESC or code == d.CANCEL:
        return

    code, vid = d.inputbox('Please give the VLAN ID.')

    if code == d.ESC or code == d.CANCEL:
        return

    default_newname = master + '.' + vid

    code, name = d.inputbox('Please name your new VLAN interface.', init=default_newname)

    if code == d.ESC or code == d.CANCEL:
        return

    vlan = VLAN(name, master, vid)

    vlan.create()

def main():
    d.set_background_title('ip-link add menu')

    choices = (
            ('bridge', 'Create a Bridge'),
            ('vlan', 'Create a VLAN'),
            )

    code, tag = d.menu('Select the type of interface you want to create.', choices=choices)

    if code == d.ESC or code == d.CANCEL:
        return

    if tag == 'bridge':
        create_bridge()
    elif tag == 'vlan':
        create_vlan()

if __name__ == '__main__':
    main()
