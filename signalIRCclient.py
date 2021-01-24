#!/usr/bin/env python3

# You need https://github.com/AsamK/signal-cli installed and working and
# paired up to your phone before any of this can be used.
#
# 1) Start signal-cli in dbus daemon mode: signal-cli -u <+phone> daemon
# 2) Start this thing.
# 3) Connect to localhost:60667 with an IRC client.

import sys
import socket
from gi.repository import GLib
from pydbus import SystemBus
import base64
import ssl
import magic
import os
import shutil
import uuid
import wget
import re
import conf
import pickle
import time




# For simplicity, accept just one client and set all the rest of it up after.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket = ssl.wrap_socket(server_socket, server_side=True, certfile=conf.cert_location, keyfile=conf.key_location)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', conf.IRC_Port))
server_socket.listen(0)
client_socket, client_address = server_socket.accept()
server_socket.close()

ircd = "signal-ircd.local"

correctPW=False
recvdNick=False
nickname = ''



def irc(action, message):
    to_b = f':{ircd} {action} {nickname} :{message}\r\n'
    client_socket.send(to_b.encode('utf-8'))


#keep looking at input until connection can be established
while (not correctPW or not recvdNick):
    #keep looking for next message
    handshake = client_socket.recv(512).decode('utf-8') 
    
    #check for password
    if handshake.startswith('PASS '):
        #check if password matches conf file
        if handshake[handshake.index('PASS ')+5:].split('\r\n')[0] == conf.Server_password:
            correctPW=True
        #send failed pw message
        else:
            irc('464','Wrong password')
            #capture connection to rate limit password checking
            time.sleep(25)
            os.execv(sys.argv[0], sys.argv)

    
    #nick being sent
    elif handshake.startswith('NICK '):
        #grab nick
        nickname = handshake[handshake.index('NICK ')+5:].split('\r\n')[0]
        recvdNick=True
    
    #if we hit user, it's probably too late, fail connection
    elif handshake.startswith('USER '):
        irc('464','Wrong password')
        time.sleep(25)
        os.execv(sys.argv[0], sys.argv)




irc('001','SIGNAL / IRC BRIDGE STARTED')
irc('251', 'There are 1 users and 0 invisible on 1 servers')
irc('255', 'I have 1 clients and 1 servers')




def ircmsg(source, message):
    for m in message.split('\r\n'):
        to_b = f':{source}!signal@{ircd} PRIVMSG {nickname} :{m}\r\n'
        client_socket.send(to_b.encode('utf-8'))


try:
    # load nick map from pickle file
    with open('nickPickle.dat', 'rb+') as filehandler:
        signal_nick_map = pickle.load(filehandler)
except EOFError:
    signal_nick_map = {}
except:
    signal_nick_map={}


bus = SystemBus()
loop = GLib.MainLoop()


signal = bus.get('org.asamk.Signal')



def receive(timestamp, source, group_id, message, attachments, **kwargs):

    print(f"Message from {source}: {message}")
    # print(f"groups from {base64.decode(group_id)}:")
    print(signal.getGroupName(group_id))

    # set a flag to see if the nickmap is updated by a new message
    nickMapUpdated = False

    sendingUserName = signal.getContactName(source)

    if sendingUserName:
        fromnick = sendingUserName.replace(' ', '_').replace(':', '')
        if not fromnick in signal_nick_map:
            signal_nick_map[fromnick] = source
            nickMapUpdated = True
    else:
        fromnick = source

    if group_id:
        print("message came from group")
        print(f"groups from {group_id}:")
        groupName = signal.getGroupName(group_id)
        groupName = 'GRP_' + groupName.replace(' ', '_').replace(':', '')
        if not groupName in signal_nick_map:
            signal_nick_map[groupName] = group_id
            nickMapUpdated = True
        message = fromnick + "- " + message
        senderName = groupName
    elif fromnick:
        senderName = fromnick
    else:
        senderName = source
    try:
        ircmsg(senderName, message)
    except:
        print("error in recieve():", sys.exc_info()[0])


    if attachments:
        print("attachments are present")
        for a in attachments:
            # use file command to determine file type
            # https://stackoverflow.com/questions/10937350/how-to-check-type-of-files-without-extensions-in-python
            print(a)

            originalfilepath = a
            filename = a.split('signal-cli/attachments/')[1]

            print(magic.from_file(originalfilepath, mime=True))
            mimetype = magic.from_file(originalfilepath, mime=True)

            filename = str(uuid.uuid1())

            if mimetype == 'image/jpeg':
                filename = filename + '.jpg'
            elif mimetype == 'image/gif':
                filename = filename + '.gif'
            elif mimetype == 'image/png':
                filename = filename + '.png'
            elif mimetype == 'video/mp4':
                filename = filename + '.mp4'

            newfilepath = '/var/www/html/signalFiles/' + filename
            shutil.copy(originalfilepath, newfilepath)
            link = conf.AttachmentStore_Hostname + conf.AttachmentStore_Path + filename

            print(link)
            ircmsg(senderName, link)

    # handle nick map updates
    if nickMapUpdated:

        with open('nickPickle.dat', 'wb+') as filehandler:
            pickle.dump(signal_nick_map, filehandler)

    return True


signal.onMessageReceived = receive


def transmit(channel, condition):
    attachments = []

    message = channel.read().decode('utf-8')
    if message == '':
        print("EOF from client, reset for new connection")
        os.execv(sys.argv[0], sys.argv)

        # sys.exit("EOF from client, exiting")
    lines = message.split('\r\n')

    message = lines[0]

    if conf.enableIRCCloudUploadHandling and "https://usercontent.irccloud-cdn.com/file/" in message:
        print("IRC IMAGE FOUND")
        # ircString = message.find("https://usercontent.irccloud-cdn.com/file/")
        url = re.search(
            "(?P<url>https?://usercontent.irccloud-cdn.com/file/[^\s]+)", message).group("url")
        message = message.replace(url, '')
        imagepath = wget.download(url)
        imagepath = '/home/signal-bridger/source/signalIRCbridge/' + imagepath
        attachments.append(imagepath)
        # os.remove(url)

    if message.startswith('PING '):
        challenge = message.split()[1]
        irc('PONG', challenge)
        print("Pingpong")
    elif message.startswith('PRIVMSG '):
        recipient = message.split()[1]
        signal_message = message.split(':', 1)[1]

        if recipient.startswith('GRP_'):
            toGroupID = signal_nick_map.get(recipient, None)
            if None:
                ircmsg(recipient, "FAILED TO FIND GROUP ID")
            else:
                signal.sendGroupMessage(signal_message, attachments, toGroupID)
                print(f"Sent to GROUP {signal_message}")
        else:
            tonumber = signal_nick_map.get(recipient, recipient)
            signal.sendMessage(signal_message, attachments, [tonumber])
            print(f"Sent to {tonumber}: {signal_message}")

        if attachments:
            os.remove(imagepath)
    else:
        irc('421', 'Unknown command')
        print(f"Unhandled IRC protocol message: {message}")
    return True





socket_ch = GLib.IOChannel(filedes=client_socket.fileno())
socket_ch.set_flags(socket_ch.get_flags() | GLib.IOFlags.NONBLOCK)
# GLib.io_add_watch(socket_ch, 0, GLib.IOCondition.IN, transmit)
GLib.io_add_watch(client_socket, GLib.IO_IN, transmit)



try:
    print("BRIDGE STARTING UP")

    loop.run()

except KeyboardInterrupt:
    sys.exit(0)

