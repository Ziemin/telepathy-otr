from telepathy.interfaces import (
    CONNECTION, CONNECTION_INTERFACE_CONTACT_LIST, \
    CONNECTION_INTERFACE_CONTACT_GROUPS, CONNECTION_INTERFACE_CONTACTS, \
    CONNECTION_INTERFACE_ALIASING, CONNECTION_INTERFACE_SIMPLE_PRESENCE)

import dbus

DBUS_PROPERTIES = "org.freedesktop.DBus.Properties"
CONTACT_LIST = CONNECTION_INTERFACE_CONTACT_LIST
CONTACTS = CONNECTION_INTERFACE_CONTACTS
ALIASING = CONNECTION_INTERFACE_ALIASING
PRESENCE = CONNECTION_INTERFACE_SIMPLE_PRESENCE

statuses = ["Connected", "Connecting", "Disconnected"]


class ConnectionMonitor:

    def __init__(self, conn):
        self.conn = conn
        conn[CONNECTION].connect_to_signal('StatusChanged',
                                           self.status_changed_handler)
        print("New connection: %s -> %s" % (self.__repr__(),
                                           statuses[conn[CONNECTION].GetStatus()]))

        self.set_contact_list()

    def set_contact_list(self):
        conn = self.conn
        if CONNECTION_INTERFACE_CONTACT_LIST in conn[DBUS_PROPERTIES].Get(CONNECTION, "Interfaces"):
            # because of key error in conn object when refering to
            # ContactListInterface
            bus = dbus.SessionBus()
            conn = bus.get_object(conn.service_name, conn.object_path)
            contact_list = dbus.Interface(conn, CONTACT_LIST)
            self.contacts = contacts = contact_list.GetContactListAttributes([CONTACT_LIST], True)
            self.print_current(conn, contacts)
        else:
            print("%s does not support contact lists" % repr(self))

    def print_current(self, con, contacts):
        aliasing = dbus.Interface(con, ALIASING)
        presence = dbus.Interface(con, PRESENCE)
        self.aliases = aliases = {}
        for c in contacts.keys():
            aliases[c] = aliasing.RequestAliases([c])[0]
        pres = presence.GetPresences(contacts.keys())
        print("Contacts: ")
        for a in aliases.keys():
            print("%s - %s" % (aliases[a], pres[a][1]))

        presence.connect_to_signal("PresencesChanged",
                                   self.presence_changed_cb)

    def presence_changed_cb(self, presences):
        for c in presences.keys():
            print("Changed presence of %s to %s" % (self.aliases[c], presences[c][1]))

    def status_changed_handler(self, status, reason):
        print("Changed status of connection %s -> %s" %
              (self.__repr__(), statuses[status]))

    def __repr__(self):
        return self.conn.service_name[len(CONNECTION)+1:]

    def __eq__(self, other):
        return repr(self) == str(other) or repr(self) == repr(other)

    def __neq__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__repr__())
