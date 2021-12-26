#!/bin/bash
dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address
/opt/signal-cli-0.10.0/bin/signal-cli --config /var/lib/signal-cli daemon --system &
# $@
/bin/bash