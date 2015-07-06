#!/usr/bin/env python

import sys
import signal
import logging
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import subprocess
import time

LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG
LOG_FILE = "/dev/stdout"
#LOG_FILE = "/var/log/syslog"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

def device_property_changed_cb(property_name, value, path, interface):
    device = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device")
    properties = device.GetProperties()

    if (property_name == "Connected"):
        action = "connected" if value else "disconnected"
        print("The device %s [%s] is %s " % (properties["Alias"],
              properties["Address"], action))
        if action == "connected":
            print("sleeping")
            time.sleep(3)
            subprocess.call(['xinput', 'set-prop',
                             'ThinkPad Compact Bluetooth Keyboard with TrackPoint',
                             'Device Accel Constant Deceleration', '0.5'])
            subprocess.call(['xinput', 'set-button-map',
                             'ThinkPad Compact Bluetooth Keyboard with TrackPoint',
                             '1 18 3 4 5 6 7'])
            print("command executed")


def shutdown(signum, frame):
    mainloop.quit()

if __name__ == "__main__":
    # shut down on a TERM signal
    signal.signal(signal.SIGTERM, shutdown)

    # start logging
    logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)
    logging.info("Starting to monitor Bluetooth connections")

    # get the system bus
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
    except Exception as ex:
        logging.error("Unable to get the system dbus: '{0}'. Exiting."
                      " Is dbus running?".format(ex.message))
        sys.exit(1)

    # listen for signals on the Bluez bus
    bus.add_signal_receiver(device_property_changed_cb, bus_name="org.bluez",
                            signal_name="PropertyChanged",
                            dbus_interface="org.bluez.Device",
                            path_keyword="path", interface_keyword="interface")
    try:
        mainloop = gobject.MainLoop()
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except:
        logging.error("Unable to run the gobject main loop")

    logging.info("Shutting down bluetooth-runner")
    sys.exit(0)
