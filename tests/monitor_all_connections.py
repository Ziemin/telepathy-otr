"""
Program to monitor states of all connections
"""

import gobject
import dbus
import dbus.glib

import telepathy
import telepathy.client

from telepathy.interfaces import CONNECTION
from telepathy.client import Connection

statuses = ["Connected", "Connection", "Disconnected"]

def findConnections():
    cons = Connection.get_connections()

    for con in cons:
        watch_connection(con)
        status = statuses[con[CONNECTION].GetStatus()]
        print("Connection: %s with status %s" % (con.service_name, status))

def watch_connection(con):
    con_name = con.service_name[len(CONNECTION):]
    con[CONNECTION].connect_to_signal('StatusChanged',
        lambda status, reason: connection_status_changed_handler(con_name, status, reason))

def connection_status_changed_handler(name, status, reason):
    print("Changed status of connection: %s to %s" % (name, statuses[status]))

def change_owner_handler(service, old, new):

    if service.startswith(CONNECTION):
        con_name = service[len(CONNECTION):]

        if len(old) == 0:
            con = Connection(service)
            watch_connection(con)
            status = statuses[con[CONNECTION].GetStatus()]
            print("new connection appeared: %s: %s" % (con_name, status))
        elif len(new) == 0:
            print("Connection died: %s" % con_name)


if __name__ == "__main__":

    loop = gobject.MainLoop()

    cons = findConnections()

    bus = dbus.Bus()

    dbus_object = bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
    dbus_object.connect_to_signal("NameOwnerChanged", change_owner_handler)

    loop.run()
