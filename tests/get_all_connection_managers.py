#!/usr/bin/python2
"""
Test program to print all available connection managers
"""


import telepathy
import telepathy.client

def getConnectionManagers():

    reg = telepathy.client.ManagerRegistry()
    reg.LoadManagers()

    protocols = reg.GetProtos()
    for p in protocols:
        print("Managers supporting protocol: %s:" % p)

        managers = reg.GetManagers(p)
        for m in managers:
            print(" - %s" % m)


if __name__ == '__main__':
    getConnectionManagers();
