
# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


from time import sleep
from line2.client import Client, OAClient, UserClient
from line2.models.types import Receiver, Type, EventType, MessageType, ChatroomType, ParameterType, WhenOALeave
from line2.models.events import Event, Message, TextMessage, ImageMessage
from line2.models.messages import Buttons
from line2.models.chatrooms import User, Room, Group
from line2.models.command import Command, Parameter
from line2.models.database import Database
from commands.coin import coinCmd
from commands.randint import randintCmd
from commands.commandlist import commandListCmd
from commands.robj import rObjCmd
from commands.mocksb import mockSBCmd
from commands.echo import echoCmd
from commands.sort import sortCmd
from commands.sort2 import sort2Cmd
from commands.sort3 import sort3Cmd
from commands.emoji import emojiCmd
from commands.vapor import vaporCmd
from commands.meme import memeCmd
from commands.space import spaceCmd
from commands.clap import clapCmd
from commands.title import titleCmd
from commands.exactreply import exactReplyCmd
from commands.regexreply import regexReplyCmd
from commands.jpeg import jpegCmd
from commands.deepfry import deepFryCmd
from commands import deepart
from commands.deepart import deepArtCmd
from commands.lunapic import lunaPicCmd
from commands.werewolf import werewolfCmd
from commands.twentyfour import twentyFourCmd
from commands.twentyfour2 import twentyFour2Cmd
from commands.byksw import bykswCmd
from traceback import format_exc
from argparse import ArgumentParser


def HandleEvent(event):
    global client
    if event.eventType == EventType.message:
        if event.messageType == MessageType.text:
            sender = event.sender
            chatroom = event.chatroom
            if event.text == '/info':
                c = event.client
                s = 'Receiver=' + Receiver.toString[event.receiver] + "\nhasOA " + str(c.hasOA) + "\nhasUser " + str(c.hasUser) + "\n"
                sender = event.sender
                chatroom = event.chatroom
                if sender is not None:
                    s = s + "Sender : " + str(sender) + "\n_2id=" + str(sender._2id) + "\nid='" + str(sender.id) + "'\nmid='" + str(sender.mid) + "'\nhasOA " + str(sender.hasOA) + "\nhasUser " + str(sender.hasUser) + "\n"
                if sender != chatroom:
                    s = s + "Chatroom : " + str(chatroom) + "\n_2id=" + str(chatroom._2id) + "\nid='" + str(chatroom.id) + "'\nmid='" + str(chatroom.mid) + "'\nhasOA " + str(chatroom.hasOA) + "\n_1hasOA " + str(chatroom._1hasOA) + "\n_2hasOA " + str(chatroom._2hasOA) + "\nhasUser " + str(chatroom.hasUser)
                event.ReplyText(s)
            if event.text == '/info2':
                c = event.client
                s = 'Receiver=' + Receiver.toString[event.receiver] + "\nhasOA " + str(c.hasOA) + "\nhasUser " + str(c.hasUser) + "\n"
                sender = event.sender
                chatroom = event.chatroom
                if sender is not None:
                    s = s + "Sender : " + str(sender) + "\n_2id=" + str(sender._2id) +  "\nname : " + str(sender.name) + "\nid='" + str(sender.id) + "'\nmid='" + str(sender.mid) + "'\nhasOA " + str(sender.hasOA) + "\nhasUser " + str(sender.hasUser) + "\n"
                if sender != chatroom:
                    s = s + "Chatroom : " + str(chatroom) + "\n_2id=" + str(chatroom._2id) + "\nname : " + str(chatroom.name) + "\nid='" + str(chatroom.id) + "'\nmid='" + str(chatroom.mid) + "'\nhasOA " + str(chatroom.hasOA) + "\nhasUser " + str(chatroom.hasUser)
                event.ReplyText(s)
            if event.text == "/name":
                event.ReplyText(str(event.sender.GetName()))
            if event.text == "/memberids":
                if event.chatroom.chatroomType != ChatroomType.user:
                    if event.sender:
                        if event.sender.isAdmin:
                            if event.chatroom.hasOA:
                                if event.chatroom.chatroomType == ChatroomType.group:
                                    event.ReplyText(str(event.client.oAClient._1client.get_group_member_ids(event.chatroom.id)))
                                else:
                                    event.ReplyText(str(event.client.oAClient._1client.get_room_member_ids(event.chatroom.id)))
                            else:
                                event.ReplyText("NOT HASOA")
                        else:
                            event.ReplyText("You're not an admin")
                    else:
                        event.ReplyText("Can't identify you")
                else:
                    event.ReplyText("Room/group only")
            if event.text == "/robjtest":
                if event.sender:
                    if True:#event.sender.isAdmin:
                        rObj = event.sender.rObj
                        if rObj:
                            rObj.SendText("Hello from /robj")
                        else:
                            event.ReplyText("%s, please type '/robj' in a room consisting of only you, our UserClient, and our OAClient" % event.sender.name)
                    else:
                        event.ReplyText("You're not an admin")
                else:
                    event.ReplyText("Can't identify you")
            elif event.text == "/clearrooms" and False:
                if event.sender:
                    if event.client.hasUser:
                        rooms = event.client.userClient._1GetAllActiveRooms()
                        for room in rooms:
                            room.Leave()
                        event.ReplyText("Left %d rooms" % len(rooms))
                        with event.client.GetCursor() as cur:
                            cur.Execute("SELECT lineMid from ChatRooms WHERE type=%s AND lineMid IS NOT NULL", (ChatroomType.room,))
                            i = 0
                            for f in cur.FetchAll():
                                room = event.client.userClient._1GetObjByLineMid(f[0])
                                if room and room.chatroomType == ChatroomType.room and room.hasUser:
                                    room.SendText("I'm leaving")
                                    room.Leave()
                                    i+=1
                            event.ReplyText("Left %d rooms (2)" % i)
                    else:
                        event.ReplyText("NOT hasUser")
                else:
                    event.ReplyText("Can't identify you")
            if event.text == "/buttons":
                try:
                    but = Buttons("ALT TEXT HEADER", "COLUMN TEXT")
                    for i in range(0, 20):
                        but.AddButton(
                            "Label %d" % i,
                            "Pressed %d" % i,
                            "\nAlt Text %d" % i
                        )
                    event.ReplyButtons(but)
                except Exception as e:
                    event.ReplyText(format_exc())
        #else:
        #    event.ReplyImageWithUrl(event.url)
        #    event.ReplyText("Image message id : " + str(event.id))
    if event.eventType == EventType.invited:
        event.Accept()
    if event.eventType == EventType.joined:
        event.chatroom.SendText("Hello I just joined")
        
port = None
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    options = arg_parser.parse_args()
    port = int(options.port)
        
global client
client = Client(
    channelAccessToken = "", 
    channelSecret = "",
    #email = "",
    #password = "",
    authToken = None, 
    certificate = None, 
    tries = 5, 
    reauthDelay = 7200, 
    adminIds = [], 
    adminMids = [], 
    dbUrl = '', 
    handler = HandleEvent,
    isMac = False,
    initAll = False,
    autoAcceptInvitation = True,
    oAAutoLeaveWhenUserLeave = True,
    whenOALeave = WhenOALeave.reinvite,
    port=port,
    pyImgurKey = "",
    pingAddress = "",
)

client.AddCommand(commandListCmd)
client.AddCommand(commandListCmd, name="commands")
client.AddCommand(rObjCmd)
client.AddCommand(rObjCmd, name='register')

client.AddCommand(coinCmd)
client.AddCommand(randintCmd)

client.AddCommand(mockSBCmd)
client.AddCommand(echoCmd)
client.AddCommand(sortCmd)
client.AddCommand(sort2Cmd)
client.AddCommand(sort3Cmd)
client.AddCommand(emojiCmd)
client.AddCommand(vaporCmd)
client.AddCommand(spaceCmd)
client.AddCommand(clapCmd)
client.AddCommand(titleCmd)

client.AddCommand(memeCmd)
client.AddAdminCommand(memeCmd)

client.AddCommand(jpegCmd)
client.AddCommand(deepFryCmd)
client.AddCommand(deepFryCmd, name="df")
deepart.daEmail = ''
deepart.daPw = ''
client.AddCommand(deepArtCmd)
client.AddCommand(deepArtCmd, name="da")
#client.AddCommand(lunaPicCmd)
#client.AddCommand(lunaPicCmd, name="lp")

client.AddContinuousTextCommand(exactReplyCmd)
client.AddCommand(exactReplyCmd)
client.AddCommand(exactReplyCmd, name="er")
client.AddContinuousTextCommand(regexReplyCmd)
client.AddCommand(regexReplyCmd)
client.AddCommand(regexReplyCmd, name="rr")

#client.AddCommand(twentyFour2Cmd)
#client.AddCommand(twentyFour2Cmd, name="242")
#client.AddContinuousTextCommand(twentyFour2Cmd)
client.AddCommand(twentyFourCmd)
client.AddCommand(twentyFourCmd, name="24")
client.AddContinuousTextCommand(twentyFourCmd)
#client.AddCommand(werewolfCmd)

client.AddCommand(bykswCmd)


def application(environ, start_response):
    global client
    return client.HandleWebhook(environ, start_response)

if __name__ == "__main__":
    client.StartOA(thread=True, port=port)
    client.StartUser(thread=5, mode=10)
    print("DONE")
    while True:
        sleep(1)