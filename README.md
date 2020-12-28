# signal to IRC bridge
Bridge between Signal and IRC'

based on https://wtf.hijacked.us/wiki/index.php/Signal-IRC_bridge
Modified mainly to support groups

requires https://github.com/AsamK/signal-cli running as a daemon

To setup follow these instructions to install signal-cli
https://github.com/AsamK/signal-cli

I then created a user signal-cli and followed these instructions to run signal-cli as a daemon: https://github.com/AsamK/signal-cli/wiki/DBus-service

Remove "--config /var/lib/signal-cli" from line 11 of https://github.com/AsamK/signal-cli/blob/master/data/signal.service before copying it over to /etc/systemd/system/

once signal-cli is running, running the ircbridge python script should get it up and running
connect your irc client to port 60667 wherever this is being run. If you're running a bouncer on localhost change '0.0.0.0' to '127.0.0.1' so that no one can access it from the outside world. The only security on it as-is that it will maintain only one connection. If you drop and it's left running, anyone will be able to access it and interact with your linked signal account.







****Notes to update


https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-getting-started

   23  pip3 install pydbus

   30  pip3 install pybase64

   35  sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
   36  pip3 install pycairo
   37  pip3 install PyGObject
   pip install vext

pip install vext.gi


sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev


# for stickers
https://pypi.org/project/signalstickers-client/
