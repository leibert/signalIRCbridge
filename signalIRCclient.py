#!/usr/bin/env python3

# pip3 install pydbus
# pip3 install python-magic
# pip3 install wget

import sys
import socket
from gi.repository import GLib
from pydbus import SystemBus
import base64
import magic
import os
import shutil
import uuid
import wget
import re 
import conf

# For simplicity, accept just one client and set all the rest of it up after.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', conf.IRC_Port))
server_socket.listen(0)
client_socket, client_address = server_socket.accept()
server_socket.close()


ircd = "signal-ircd.local"
handshake = client_socket.recv(512).decode('utf-8')
while not 'NICK ' in handshake:
    # We don't care about USER.
    handshake = client_socket.recv(512).decode('utf-8')
nickname = handshake[handshake.index('NICK ')+5:].split('\r\n')[0]

def irc(action, message):
    to_b = f':{ircd} {action} {nickname} :{message}\r\n'
    client_socket.send(to_b.encode('utf-8'))

irc('001', 'Signal-IRC bridge ready. IF THIS CONNECTION DROPS ALL YOUR MESSAGES COULD BELONG TO THE WORLD')
irc('251', 'There are 1 users and 0 invisible on 1 servers')
irc('255', 'I have 1 clients and 1 servers')

def ircmsg(source, message):
    for m in message.split('\r\n'):
        to_b = f':{source}!signal@{ircd} PRIVMSG {nickname} :{m}\r\n'
        client_socket.send(to_b.encode('utf-8'))

# This can be prepopulated.
signal_nick_map = {}

bus = SystemBus()
loop = GLib.MainLoop()


signal = bus.get('org.asamk.Signal')
def receive(timestamp, source, group_id, message, attachments):
    print(f"Message from {source}: {message}")
    # print(f"groups from {base64.decode(group_id)}:")
    print(signal.getGroupName(group_id))

    sendingUserName = signal.getContactName(source)

    if sendingUserName:
        fromnick = sendingUserName.replace(' ', '_').replace(':', '')
        if not fromnick in signal_nick_map:
            signal_nick_map[fromnick] = source
    else:
        fromnick=source











    if group_id:
        print("message came from group")
        print(f"groups from {group_id}:")
        groupName=signal.getGroupName(group_id)
        groupName = 'GRP_' + groupName.replace(' ', '_').replace(':', '')
        if not groupName in signal_nick_map:
            signal_nick_map[groupName] = group_id
        message = fromnick +"- "+message
        senderName=groupName
    elif fromnick:
        senderName=fromnick
    else:
        senderName=source

    ircmsg(senderName,message)


    if attachments:
        print("attachments are present")
        for a in attachments:
            #use file command to determine file type
            #https://stackoverflow.com/questions/10937350/how-to-check-type-of-files-without-extensions-in-python
            print(a)

            originalfilepath = a
            filename = a.split('signal-cli/attachments/')[1]


            print(magic.from_file(originalfilepath, mime=True))
            mimetype = magic.from_file(originalfilepath, mime=True)

            filename=str(uuid.uuid1())

            if mimetype == 'image/jpeg':
                filename=filename+'.jpg'
            elif mimetype == 'image/gif':
                filename=filename+'.gif'
            elif mimetype == 'image/png':
                filename=filename+'.png'
            elif mimetype == 'video/mp4':
                filename=filename+'.mp4'

            newfilepath = '/var/www/html/signalFiles/' + filename
            shutil.copy(originalfilepath, newfilepath)
            link = conf.AttachmentStore_Hostname+conf.AttachmentStore_Path+filename

            print(link)
            ircmsg(senderName,link)







    return True

signal.onMessageReceived = receive

def transmit(channel, condition):
    attachments =[]


    message = channel.read().decode('utf-8')
    if message == '':
        sys.exit("EOF from client, exiting")
    lines = message.split('\r\n')
    assert lines[-1] == '' and len(lines) == 2,\
        f"If this fails we need more complex line handling: {lines}"
    message = lines[0]


    if conf.enableIRCCloudUploadHandling and "https://usercontent.irccloud-cdn.com/file/" in message:
        print ("IRC IMAGE FOUND")
        # ircString = message.find("https://usercontent.irccloud-cdn.com/file/")
        url = re.search("(?P<url>https?://usercontent.irccloud-cdn.com/file/[^\s]+)", message).group("url")
        message=message.replace(url,'')
        imagepath = wget.download(url)
        imagepath = '/home/signal-bridger/source/signalIRCbridge/'+imagepath
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
            toGroupID=signal_nick_map.get(recipient, None)
            if None:
                ircmsg(recipient,"FAILED TO FIND GROUP ID")
            else:
                signal.sendGroupMessage(signal_message,attachments,toGroupID)
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
GLib.io_add_watch(socket_ch, 0, GLib.IOCondition.IN, transmit)


try:
    print("BRIDGE STARTING UP")

    loop.run()
except KeyboardInterrupt:
    sys.exit(0)

