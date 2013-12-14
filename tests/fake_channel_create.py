import telepathy
from telepathy.client import Connection
from telepathy.interfaces import CHANNEL, \
        CHANNEL_TYPE_TEXT, CHANNEL_INTERFACE_MESSAGES
import dbus
import gobject

from telepathy.server import Channel

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

channel = None


class FakeChannel(telepathy.server.DBusProperties):

    def __init__(self, *args):
        telepathy.server.DBusProperties.__init__(self)

        self._implement_property_get(CHANNEL, {
            'Interfaces': self.GetInterfaces
        })

        self._implement_property_get(CHANNEL, {
            'ChannelType': self.GetChannelType
        })

        self._implement_property_get(CHANNEL, {
            'TargetHandle': lambda: 1
        })

        self._implement_property_get(CHANNEL, {
            'TargetID': "XMPP"
        })

        self._implement_property_get(CHANNEL, {
            'TargetHandleType': lambda: 1
        })

        self._implement_property_get(CHANNEL, {
            'Requested': lambda: False
        })

        self._implement_property_get(CHANNEL, {
            'InitiatorHandle': lambda: 1
        })

        self._implement_property_get(CHANNEL, {
            'InitiatorID': lambda: "ID"
        })

        self._implement_property_get(CHANNEL, {
            'InitiatorHandle': lambda: 1
        })

        self._implement_property_get(CHANNEL_INTERFACE_MESSAGES, {
            'SupportedContentTypes': lambda: ["text/plain", "text/html"]
        })

        self._implement_property_get(CHANNEL_INTERFACE_MESSAGES, {
            'MessageTypes': lambda: [1]
        })

        self._implement_property_get(CHANNEL_INTERFACE_MESSAGES, {
            'MessagePartSupportFlags': lambda: 1
        })

        self._implement_property_get(CHANNEL_INTERFACE_MESSAGES, {
            'PendingMessages': lambda: []
        })

        self._implement_property_get(CHANNEL_INTERFACE_MESSAGES, {
            'DeliveryReportingSupport': lambda: 1
        })

    def SendMessage(self, mess, flags):
        return ""

    def GetPendingMessageContent(self, message, pargs):
        pass

    def AcknowledgePendingMessages(self, ids):
        pass

    def Close(self):
        pass

    def GetChannelType(self):
        return CHANNEL_TYPE_TEXT

    def GetHandle(self):
        return (1, 1)

    def GetInterfaces(self):
        return [CHANNEL, CHANNEL_TYPE_TEXT, CHANNEL_INTERFACE_MESSAGES]


def publish_channel(name):
    bus_name = '.'.join([CHANNEL, name])
    object_path = '/' + bus_name.replace('.', '/')
    bus_name = dbus.service.BusName(bus_name, bus=dbus.SessionBus())
    global channel
    channel = FakeChannel(bus_name, object_path)

    return False

if __name__ == "__main__":
    loop = gobject.MainLoop()

    con = Connection.get_connections()[0]
    con.create_channel

    gobject.timeout_add(0, publish_channel, "MyFakeChannel")

    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
