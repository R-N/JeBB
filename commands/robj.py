# -*- coding: utf-8 -*-
from line2.models.types import ChatroomType
from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

groupOnly = False

def RObj(message, options, text=''):
    if not message.client.hasUser or not message.client.hasOA or not message.client.oAClient.obj:
        message.ReplyText("Sorry, this feature is unavailable")
        return CommandResult.Failed()
    client = message.client
    chatroom = message.chatroom
    sender = message.sender
    if chatroom.chatroomType == ChatroomType.user:
        message.ReplyText("This is a private chat")
        return CommandResult.Failed()
    if groupOnly and chatroom.chatroomType == ChatroomType.room:
        message.ReplyText("This needs to be a group")
        return CommandResult.Failed()
    if not sender or not sender.name:
        message.ReplyText("Sorry, we can't identify you")
        return CommandResult.Failed()
    if not chatroom.hasUser:
        message.ReplyText("You need to have our User Account Bot here.")
        return CommandResult.Failed()
    members = chatroom.members
    if len(members) == 0:
        message.ReplyText("Sorry, we couldn't get member list")
        return CommandResult.Failed()
    if client.oAClient.obj not in members:
        message.ReplyText("Our Official Account Bot is not here. I'll try to invite it. Please retry after it joined")#\n%s\n%s" % (members, client.oAClient.obj))
        try:
            chatroom.Invite(client.oAClient.obj)
        except Exception:
            pass
        return CommandResult.Failed()
    if len(members) > 3:
        message.ReplyText("There can only be you, me, and the other bot")
        return CommandResult.Failed()
    sender.rObj = chatroom
    message.ReplyText("This room has been registered as %s's RObj" % sender.name)
    return CommandResult.Done()
        
    
        

rObjCmd = Command(
    'robj',
    RObj,
    desc='Register your rObj'
)
