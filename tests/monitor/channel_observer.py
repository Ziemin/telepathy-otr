
import telepathy
import dbus
from telepathy.server import Observer
from telepathy.interfaces import CLIENT, CLIENT_OBSERVER, CHANNEL

class ChannelObserver(Observer, telepathy.server.DBusProperties):

    def __init__(self, *args):
        telepathy.server.Observer.__init__(self, *args)
        telepathy.server.DBusProperties.__init__(self)

        self._implement_property_get(CLIENT, {
            'Interfaces': lambda: [CLIENT_OBSERVER]
        })
        self._implement_property_get(CLIENT_OBSERVER, {
            'ObserverChannelFilter': lambda: dbus.Array([
                dbus.Dictionary({
                    "org.freedesktop.Telepathy.Channel.ChannelType":
                    "org.freedesktop.Telepathy.Channel.Type.Text"
                }, signature='sv')
            ], signature='a{sv}')
        })

    def ObserveChannels(self, account, connection, channels, dispatch_operation,
                        requests_satisfied, observer_info):
        print("Incoming channels on: %s" % (connection.replace('/', '.')[1:]))
        for object, props in channels:
            print(" - %s :: %s - requested: %s" % (props[CHANNEL + '.ChannelType'],
                                                   props[CHANNEL + '.TargetID'],
                                            props[CHANNEL + '.Requested']))

