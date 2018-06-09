#!/usr/bin/env python3

import dialog

import os
from pyroute2 import IPRoute, IPDB
import subprocess

d = dialog.Dialog()

ipdb = IPDB()

class Bridge():
    def __init__(self, name, interfaces=[]):
        self.name = name
        self.interfaces = interfaces

    def create(self):
        global ipdb
        with ipdb.create(kind='bridge', ifname=self.name) as master:
            for slave in self.interfaces:
                master.add_port(ipdb.interfaces[slave])

class VLAN():
    def __init__(self, name, master, vid):
        self.name = name
        self.master = master
        self.vid = int(vid)

    def create(self):
        global ipdb
        underlying = ipdb.interfaces[self.master]
        ipdb.create(
            kind='vlan',
            ifname=self.name,
            link=underlying,
            vlan_id=self.vid
        ).commit()

class MACVLAN():
    def __init__(self, name, master, mode):
        self.name = name
        self.master = master
        self.mode = mode

    def create(self):
        global ipdb
        underlying = ipdb.interfaces[self.master]
        ipdb.create(
            kind='macvlan',
            ifname=self.name,
            link=underlying,
            mode=self.mode
        ).commit()

def create_bridge():
    choices = [(str(i), '', False) for i in ipdb.by_name.keys()]

    code, interfaces = d.checklist('Select the interfaces to add to the bridge.', choices=choices)

    if code == d.ESC or code == d.CANCEL:
        return

    code, name = d.inputbox('Please name your new bridge.')

    if code == d.ESC or code == d.CANCEL:
        return

    bridge = Bridge(name, interfaces)

    bridge.create()

def create_vlan():
    choices = [(str(i), '') for i in ipdb.by_name.keys()]

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

def create_macvlan():
    choices = [(str(i), '') for i in ipdb.by_name.keys()]

    code, master = d.menu('Select the master interface to use.', choices=choices)

    if code == d.ESC or code == d.CANCEL:
        return

    code, name = d.inputbox('Please name your new MACVLAN interface.')

    if code == d.ESC or code == d.CANCEL:
        return

    choices = [
            ('private', 'Private'),
            ('vepa', 'VEPA'),
            ('bridge', 'Bridge'),
            ('passthru', 'Passthrough'),
            ('source', 'Source'),
            ]

    code, mode = d.menu('Select the mode of MACVLAN interface.', choices=choices)

    macvlan = MACVLAN(name, master, mode)

    macvlan.create()

def main():
    d.set_background_title('ip-link add menu')

    choices = (
            ('bridge', 'Create a Bridge'),
            ('vlan', 'Create a VLAN'),
            ('macvlan', 'Create a MACVLAN'),
            )

    code, tag = d.menu('Select the type of interface you want to create.', choices=choices)

    if code == d.ESC or code == d.CANCEL:
        return

    if tag == 'bridge':
        create_bridge()
    elif tag == 'vlan':
        create_vlan()
    elif tag == 'macvlan':
        create_macvlan()

if __name__ == '__main__':
    main()
