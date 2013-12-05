""" Global Monitor.

Purpose of this program is to monitor all active connection,
contacts and channels related to them

"""

import telepathy
import gobject
import dbus

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

from connection_monitor import ConnectionMonitor
from channel_observer import ChannelObserver
from telepathy.client import Connection
from telepathy.interfaces import (
    CONNECTION, CLIENT)


statuses = ["Connected", "Connecting", "Disconnected"]

class Monitor:

    def __init__(self):
        self.loop = gobject.MainLoop()

        self.con_monitors = con_monitors = set()
        for con in Connection.get_connections():
            con_monitors.add(ConnectionMonitor(con))

        bus = dbus.Bus()
        dbus_object = bus.get_object("org.freedesktop.DBus",
                                     "/org/freedesktop/DBus")
        dbus_object.connect_to_signal("NameOwnerChanged",
                                      self.change_owner_handler)


    def run(self):
        gobject.timeout_add(0, publish_observer, "TextChannelObserver")

        try:
            self.loop.run()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            self.stop()

    def change_owner_handler(self, service, old, new):

        if service.startswith(CONNECTION) and service[len(CONNECTION)] == '.':
            if len(old) == 0:
                con = Connection(service)
                self.con_monitors.add(ConnectionMonitor(con))
            elif len(new) == 0:
                print("Connection died: %s" % service[len(CONNECTION)+1:])
                try:
                    self.con_monitors.remove(service[len(CONNECTION)+1:])
                except KeyError as ke:
                    print("Key error while removing: %s" % (ke.message))


    def stop(self):
        self.loop.quit()


def publish_observer(name):
    bus_name = '.'.join([CLIENT, name])
    object_path = '/' + bus_name.replace('.', '/')

    bus_name = dbus.service.BusName(bus_name, bus=dbus.SessionBus())
    ChannelObserver(bus_name, object_path)

    return False


if __name__ == "__main__":
    gobject.timeout_add(2, publish_observer, "SimpleTextChannelObserver")
    Monitor().run()
