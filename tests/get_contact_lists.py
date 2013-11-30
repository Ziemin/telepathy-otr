"""
Program printing a contact list for some jabber connection
from gabble
"""

import sys
import dbus.mainloop.glib
import getpass
import gobject

import telepathy
import telepathy.client
from telepathy.interfaces import (
    CONN_MGR_INTERFACE, CONNECTION, CONNECTION_INTERFACE_CONTACT_GROUPS,
    CHANNEL_TYPE_CONTACT_LIST, CONN_INTERFACE_ALIASING)
from telepathy.constants import (
    CONNECTION_HANDLE_TYPE_CONTACT, CONNECTION_HANDLE_TYPE_LIST,
    CONNECTION_STATUS_CONNECTED, CONNECTION_STATUS_DISCONNECTED)

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)


DBUS_PROPERTIES = 'org.freedesktop.DBus.Properties'
statuses = ["Connected", "Connecting", "Disconnected"]

class ContactListMonitor:

    def __init__(self, loop):
        self.loop = loop

        self.conn = get_connection()
        if(self.conn == None):
            print("No connection established")
            sys.exit(1)
        else:
            print("Acquired connection %s" % (self.conn.service_name))

        self.conn[CONNECTION].connect_to_signal(
            'StatusChanged', self._status_changed_cb)

    def _status_changed_cb(self, state, reason):
        if state == CONNECTION_STATUS_DISCONNECTED:
            print("Disconnected: %s" % reason)
            self.stop()

    def _get_list_channel(self, name):
        handle = self.conn[CONNECTION].RequestHandles(
            CONNECTION_HANDLE_TYPE_LIST, [name])[0]
        chan_path = self.conn[CONNECTION].RequestChannel(
            CHANNEL_TYPE_CONTACT_LIST, CONNECTION_HANDLE_TYPE_LIST, handle, True)
        channel = telepathy.client.Channel(self.conn.service_name, chan_path)
        return channel

    def _start(self):
        print("start")
        channel = self._get_list_channel("subscribe")
        current, local_pending, remote_pending = (
            channel['org.freedesktop.Telepathy.Channel.Interface.Group'].GetAllMembers())
        names = self.conn[CONNECTION].InspectHandles(
                CONNECTION_HANDLE_TYPE_CONTACT, current)

        channel['org.freedesktop.Telepathy.Channel.Interface.Group'].connect_to_signal(
            'MembersChanged', self.members_changed_handler)

        for handle, name in zip(current, names):
            print("% 5d: %s" % (handle, name))

    def members_changed_handler(message, added, removed, local_pending,
                                remote_pending, actor, reason):
        print(added, removed, message, local_pending, remote_pending, actor, reason)


    def run(self):
        print("Starting monitor")
        self.conn[CONNECTION].Connect()

        try:
            self._start()
            self.loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("Stopping")
        self.loop.quit()


def get_connection():
    cons = telepathy.client.Connection.get_connections()
    for con in cons:
        if con[CONNECTION].GetStatus() == CONNECTION_STATUS_CONNECTED:
            return con


if __name__ == '__main__':

    loop = gobject.MainLoop()
    ContactListMonitor(loop).run()
