# signalIRCbridge
Bridge between Signal and IRC'

based on https://wtf.hijacked.us/wiki/index.php/Signal-IRC_bridge
Modified mainly to support groups

requires https://github.com/AsamK/signal-cli running as a daemon

To setup follow these instructions to install signal-cli
https://github.com/AsamK/signal-cli

I then created a user signal-cli and followed these instructions to run signal-cli as a daemon: https://github.com/AsamK/signal-cli/wiki/DBus-service

Remove "--config /var/lib/signal-cli" from line 11 of https://github.com/AsamK/signal-cli/blob/master/data/signal.service before copying it over to /etc/systemd/system/



packages for bridger:
pip3 install pydbus
sudo apt-get install libunixsocket-java


once signal-cli is running, running the ircbridge python script should get it up and running
connect your irc client to port 60667 wherever this is being run. If you're running a bouncer on localhost change '0.0.0.0' to '127.0.0.1' so that no one can access it from the outside world. The only security on it as-is that it will maintain only one connection. If you drop and it's left running, anyone will be able to access it and interact with your linked signal account.
