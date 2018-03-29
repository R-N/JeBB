import utils

from traceback import format_exc, print_exc
from tempfile import gettempdir
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage as _TextMessage, TextSendMessage, TemplateSendMessage, TemplateAction, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, ButtonsTemplate, PostbackEvent, CarouselTemplate, CarouselColumn, LeaveEvent, FollowEvent, UnfollowEvent, JoinEvent, ImageSendMessage, ImageMessage as _ImageMessage

from .api.line_0_10_0.ttypes import TalkException, MIDType, OpType, IdentityProvider, Message as _Message, ContentType
from requests.exceptions import (ReadTimeout, Timeout)

from .api.api import LineAPI, needAuthErrors
from .models.types import Receiver, MessageType, ChatroomType, EventType, UserStatus, UserRelation, WhenOALeave, CommandType, CommandResultType, CommandContinuousCallType
from .models.events import Event, Joined, Invited, Left, Followed, Unfollowed, Message, TextMessage, ImageMessage, Update, Button, Buttons, StickerMessage, LocationMessage, AudioMessage, VideoMessage, FileMessage, ContactMessage
from .models.chatrooms import User, Room, Group, StartRObj
from .models.database import Database
from .models.command import CommandResult, CommandStack
from .models.content import Image
from .utils import IsEmpty, emailRegex, Lock, Alphanumeric, EscapeNames, Acquire, InitAtExit, CreateBody, Clean
from .oaclient import OAClient
from .userclient import UserClient

from requests import get as RequestsGet, post as RequestsPost

from time import time, sleep

from socket import timeout

from threading import Thread, current_thread, Condition

from ssl import SSLError
from thrift.protocol.TProtocol import TProtocolException

from wsgiref.simple_server import make_server

from re import compile, DOTALL

from random import randint

import os
from pyimgur import Imgur
from .models.content import UploadPyImgur, Download, ScaleyUrl

from json import loads, dumps
from shutil import copyfileobj
from codecs import encode, decode


class Client(object):
    
    def __init__(self, channelAccessToken = None, channelSecret = None, email = "", password = "", authToken = "", certificate = "", tries = 5, reauthDelay = 7200, adminIds = [], adminMids = [], dbUrl = None, handler = None, isMac = True, initAll = False, autoAcceptInvitation = True, oAAutoLeaveWhenUserLeave = True, whenOALeave = WhenOALeave.reinvite, oAMid = None, userId = None, userMid = None, comName = "USER", port=None, pyImgurKey = None, oAName="our OA bot", userName="our User bot", pingAddress = None, pingInterval = 180):
        object.__init__(self)
        InitAtExit()
        self.port = port
        self._1adminCommands = {}
        self._1commands = {}
        self._1continuousTextCommands = []
        self._1continuousImageCommands = []
        self._1continuousAudioCommands = []
        self._1continuousVideoCommands = []
        self._1continuousFileCommands = []
        self._1continuousStickerCommands = []
        self._1imageWaitingCommands = {}
        self.lock = Lock()
        self.handler = handler
        self.oAClient = None
        self.userClient = None
        self.db = None
        self.main = 0
        self.hasCommands = False
        self.hasAdminCommands = False
        self.hasContinuousTextCommands = False
        self.hasContinuousImageCommands = False
        self.hasContinuousAudioCommands = False
        self.hasContinuousVideoCommands = False
        self.hasContinuousFileCommands = False
        self.hasContinuousStickerCommands = False
        self.groups = []
        self.rooms = []
        self.users = []
        self._1objectsUserByMsgId = {}
        self._1objectsOAByMsgId = {}
        self._1senderObjectsUserByMsgId = {}
        self._1senderObjectsOAByMsgId = {}
        self._1objectsByLineId = {}
        self._1objectsByLineMid = {}
        self._1objectsByRId = {}
        self._1objectsByUId = {}
        self._1headers = {}
        self._1waitingRoom = {}
        self.getUserClientThread = None
        self.oAObj = None
        self.userObj = None
        self._1code = None
        
        self.eCond = Condition()
        self.eventQueue = []
        self.mLock = Lock()
        self.messages = {}
        self.pingAddress = pingAddress
        self.pingInterval = pingInterval
        
        self._1dbUrl = dbUrl
        if not IsEmpty(dbUrl):
            self.CreateDatabase(dbUrl)
            
        if not isinstance(adminIds, list):
            adminIds = []
            
        if not isinstance(adminMids, list):
            adminMids = []

        self.oAName = oAName
        self.userName = userName
        
        self._1channelAccessToken = channelAccessToken
        self._1channelSecret = channelSecret
        self._1tries = int(self.TryDBVar("tries", tries))
        #self._1email = self.TryDBVar("email", email)
        #self._1password = self.TryDBVar("password", password)
        self._1email = email
        self._1password = password
        self._1authToken = self.TryDBVar("authToken", authToken)
        self._1certificate = self.TryDBVar("certificate", certificate)
        self._1reauthDelay = int(self.TryDBVar("reauthDelay", reauthDelay))
        self._1isMac = bool(self.TryDBVar("isMac", isMac))
        self._1autoAcceptInvitation = bool(self.TryDBVar("autoAcceptInvitation", autoAcceptInvitation))
        self._1whenOALeave = bool(self.TryDBVar("whenOALeave", whenOALeave))
        self._1oAAutoLeaveWhenUserLeave = bool(self.TryDBVar("autoAcceptInvitation", oAAutoLeaveWhenUserLeave))
        self._1oAMid = self.TryDBVar("oAMid", oAMid)
        self._1userId = self.TryDBVar("userId", userId)
        self._1userMid = self.TryDBVar("userMid", userMid)
        self._1comName = self.TryDBVar("comName", comName)
        self._1pyImgurKey = self.TryDBVar("pyImgurKey", pyImgurKey)
        
        self.adminIds = adminIds
        self.adminMids = adminMids
        self.adminObjs = []
        self.hasAdmins = len(adminIds) > 0 or len(adminMids) > 0
        self.hasAdminCommands = False
        self.inited = 5
        self.code = None
        self._1started = False
        self.startCond = Condition()
        self.Init(initAll)
        
    @property
    def started(self):
        return self._1started
    
    @started.setter
    def started(self, value):
        with self.startCond:
            self._1started = value
            if value:
                print("STARTED")
                self.startCond.notifyAll()
        
    def GetObjByRId(self, rId):
        if rId is None:
            return
        rId = int(rId)
        if rId in self._1objectsByRId:
            return self._1objectsByRId[rId]
        if self.db is None:
            return
        f = None
        with self.GetCursor() as cur:
            cur.Execute("SELECT lineId, lineMid FROM ChatRooms WHERE id=%s", (rId,))
            f = cur.FetchOne()
            if f is None:
                return
        if f[1] and self.hasUser:
            return self.userClient._1GetObjByLineMid(f[1])
        if f[0] and self.hasOA:
            return self.oAClient._1GetObjByLineId(f[0])
    
    def GetObjByUId(self, uId):
        if uId is None:
            return
        uId = int(uId)
        if uId in self._1objectsByUId:
            return self._1objectsByUId[uId]
        if self.db is None or not self.hasUser:
            return
        f = None
        with self.GetCursor() as cur:
            cur.Execute("SELECT lineMid FROM Users WHERE id=%s", (uId,))
            f = cur.FetchOne()
            if f is None:
                return
        return self.userClient._1GetObjByLineMid(f[0])
        
        
    @property
    def oAAutoLeaveWhenUserLeave(self):
        return self._1oAAutoLeaveWhenUserLeave
    
    def SetTextVar(self, name, value):
        if self.db is not None:
            with self.GetCursor() as cur:
                cur.SetTextVar(name, value)
    
    @oAAutoLeaveWhenUserLeave.setter
    def oAAutoLeaveWhenUserLeave(self, value):
        self.SetTextVar("oAAutoLeaveWhenUserLeave", value)
        self._1oAAutoLeaveWhenUserLeave = value
        
    @property
    def dbUrl(self):
        return self._1dbUrl
    
    @dbUrl.setter
    def dbUrl(self, value):
        if value != self._1dbUrl:
            self.SetTextVar("dbUrl", value)
            self._1dbUrl = value
            if not IsEmpty(value):
                self.CreateDatabase(value)
                    
    def TryDBVar(self, name, value, cur=None, commit=True):
        if cur is None:
            if self.db is None:
                return value
            cur = self.GetCursor()
            commit = True
        if IsEmpty(value):
            return cur.GetTextVar(name)
        else:
            cur.SetTextVar(name, str(value), commit=commit)
        return value
        
    @property
    def hasOA(self):
        return self.oAClient is not None
    
    @property
    def hasUser(self):
        return self.userClient is not None and self.userClient.ready
        
        
    @property
    def whenOALeave(self):
        return self._1whenOALeave
    
    @whenOALeave.setter
    def whenOALeave(self, value):
        self.SetTextVar("whenOALeave", value)
        self._1whenOALeave = value
        
    def GetPyImgurClient(self):
        if self.pyImgurKey is None:
            return
        return Imgur(self.pyImgurKey)
    
    def UploadPyImgur(self, bytes):
        if self.pyImgurKey is None:
            return
        return UploadPyImgur(self.GetPyImgurClient(), bytes)
        
    @property
    def pyImgurKey(self):
        return self._1pyImgurKey
    
    @pyImgurKey.setter
    def pyImgurKey(self, value):
        self.SetTextVar("pyImgurKey", value)
        self._1pyImgurKey = value
        
    @property
    def comName(self):
        return self._1comName
    
    @comName.setter
    def comName(self, value):
        self.SetTextVar("comName", value)
        self._1comName = value
        
    @property
    def isMac(self):
        return self._1isMac
    
    @isMac.setter
    def isMac(self, value):
        self.SetTextVar("isMac", value)
        self._1isMac = value
        
    @property
    def autoAcceptInvitation(self):
        return self._1autoAcceptInvitation
    
    @autoAcceptInvitation.setter
    def autoAcceptInvitation(self, value):
        self.SetTextVar("autoAcceptInvitation", value)
        self._1autoAcceptInvitation = value
        
    @property
    def reauthDelay(self):
        return self._1reauthDelay
    
    @reauthDelay.setter
    def reauthDelay(self, value):
        self.SetTextVar("reauthDelay", value)
        self._1reauthDelay = value
        
    @property
    def certificate(self):
        return self._1certificate
    
    @certificate.setter
    def certificate(self, value):
        print("TRYING TO SET CERTIFICATE WITH " + str(value))
        self.SetTextVar("certificate", value)
        self._1certificate = value
        
    @property
    def authToken(self):
        return self._1authToken
    
    @authToken.setter
    def authToken(self, value):
        print("TRYING TO SET AUTHTOKEN WITH " + str(value))
        self.SetTextVar("authToken", value)
        self._1authToken = value
        
    @property
    def password(self):
        return self._1password
    
    @password.setter
    def password(self, value):
        self.SetTextVar("password", value)
        self._1password = value
        
    @property
    def email(self):
        return self._1email
    
    @email.setter
    def email(self, value):
        self.SetTextVar("email", value)
        self._1email = value
        
    @property
    def oAMid(self):
        return self._1oAMid
    
    @oAMid.setter
    def oAMid(self, value):
        self.SetTextVar("oAMid", value)
        self._1oAMid = value
        
    @property
    def userId(self):
        return self._1userId
    
    @userId.setter
    def userId(self, value):
        self.SetTextVar("userId", value)
        self._1userId = value
        
    @property
    def userMid(self):
        return self._1userMid
    
    @userMid.setter
    def userMid(self, value):
        self.SetTextVar("userMid", value)
        self._1userMid = value
        
    @property
    def tries(self):
        return self._1tries
    
    @tries.setter
    def tries(self, value):
        self.SetTextVar("tries", value)
        self._1tries = value
        
    @property
    def channelSecret(self):
        return self._1channelSecret
    
    @channelSecret.setter
    def channelSecret(self, value):
        self.SetTextVar("channelSecret", value)
        self._1channelSecret = value
        
    @property
    def channelAccessToken(self):
        return self._1channelAccessToken
    
    @channelAccessToken.setter
    def channelAccessToken(self, value):
        self.SetTextVar("channelAccessToken", value)
        self._1channelAccessToken = value
            
    def Init(self, initAll = False):
        with Acquire(self.lock):
            if self.db is None and self.dbUrl is not None:
                self.CreateDatabase(self.dbUrl)
            if self.oAClient is None and not IsEmpty(self.channelAccessToken) and not IsEmpty(self.channelSecret):
                self.oAClient = OAClient(self)
            canGetUserClient = self.userClient is None and (self.getUserClientThread is None or not self.getUserClientThread.isAlive()) and ((not IsEmpty(self.authToken) and not IsEmpty(self.certificate)) or (not IsEmpty(self.email) and not IsEmpty(self.password)))
            print("INITB1")
            if self.oAClient is None and canGetUserClient:
                #self.getUserClientThread = Thread(target=self.ThreadExceptionCatcher, args=[self.GetUserClient, [self.email, self.password, self.authToken, self.certificate, self.tries, self.reauthDelay, self.adminMids]])
                #self.getUserClientThread.start()
                self.GetUserClient()
            print("INITB2")
            if canGetUserClient:
                if self.oAClient is not None:
                    self.oAClient.Start(thread=True, port=self.port)
                with Acquire(self.lock):
                    self.GetUserClient()
        print("INITA1")
        if self.oAClient is not None:
            with Acquire(self.oAClient.lock):
                for id in self.adminIds:
                    o = self.oAClient._1GetObjByLineId(id)
                    self.adminObjs.append(o)
                    self.oAClient.adminObjs.append(o)
        print("INITA2")
        if self.userClient is not None:
            with Acquire(self.userClient.lock):
                for mid in self.adminMids:
                    o = self.userClient._1GetObjByLineMid(mid)
                    self.adminObjs.append(o)
                    self.userClient.adminObjs.append(o)
            if self.oAClient is None or self.userClient is None:
                self.inited = 5
            elif self.oAClient.mid is None:
                self.inited = 0
            else:
                self.oAClient.obj = self.userClient._1GetObjByLineMid(self.oAClient.mid)
                if self.userClient.id is None:
                    self.inited = 2
                else:
                    self.userClient.obj = self.oAClient._1GetObjByLineId(self.userClient.id)
                    if self.userClient.mid is None:
                        self.inited = 4
                    else:
                        self.inited = 5
            if initAll:
                self.Thread(self.RefreshAll)
                #self.RefreshAll()
            elif self.userClient is not None:
                if self.autoAcceptInvitation:
                    self.Thread(self.userClient._1AcceptAllGroupInvitations)
                else:
                    self.Thread(self.userClient._1GetAllGroupsInvited)
                    #self.userClient._1GetAllGroupsInvited()
        StartRObj(self)
        print("INIT DONE")
            
            
                            
    @property
    def cursor(self):
        return self.GetCursor()
            
    def GetCursor(self):
        if True:#with self.lock:
            return self.db.GetCursor()
    
    def GetUserClient(self):
        uc = UserClient(self)
        if True:#with self.lock:
            self.userClient = uc
            self.getUserClientThread = None
            self.authToken = self.userClient.authToken
            self.certificate = self.userClient.certificate
            
    def HandleWebhook(self, environ, start_response):
        if self.hasOA:
            return self.oAClient.HandleWebhook(environ, start_response)
        start_response('503 Service Unavailable', [])
        return CreateBody('Service Unavailable')
    
    def Thread(self, method, args=[], kwargs = {}, start = True):
        t = Thread(target=self.ThreadExceptionCatcher, args=[method, args, kwargs])
        if start:
            t.start()
        return t
    
            
    def ThreadExceptionCatcher(self, method, args=[], kwargs={}):
        try:
            return (True, method(*args, **kwargs))
        except TalkException as e:
            print_exc()
            self.Report("[Client.ThreadExceptionCatcher]\n" + str(e))
            if e.code in needAuthErrors:
                self.userClient._1UpdateAuthToken()
        except Exception:
            self.Report("[Client.ThreadExceptionCatcher]\n" + format_exc())
        return (False, None)
    
    _1init1Regex = compile("\[Init1\] ([^ ]+)")
    _1init3Regex = compile("\[Init3\] ([^ ]+)")
    
    def GetObjByLineId(self, id):
        if self.hasOA:
            return self.oAClient._1GetObjByLineId(id)
        
    def GetObjByLineMid(self, mid):
        if self.hasUser:
            return self.userClient._1GetObjByLineMid(mid)
        
    def RefreshAll(self):
        if self.hasUser:
            return self.userClient._1RefreshAll()
        return False
    
    def Init2(self, event):
        if self.inited == 0 and event.chatroom.chatroomType != ChatroomType.user and event.chatroom.hasUser and event.chatroom.hasOA:
            self._1code = str(randint(1000, 9999))
            self.inited = 1
            self._1expectedChatroomMid = event.chatroom.mid
            self.oAClient._1SendText(event.chatroom, "[Init1] " + self._1code + " \nPlease ignore this message.")
        if self.inited == 1 and event.chatroom.mid == self._1expectedChatroomMid: 
            if event.eventType == EventType.message and event.messageType == MessageType.text:
                mI1 = self._1init1Regex.match(event.text)
                if mI1 is not None and mI1.group(1) == self._1code:
                    self.oAClient.mid = event.sender.mid
                    self.oAClient.obj = self.userClient._1GetObjByLineMid(self.oAClient.mid)
                    if self.userClient.id is None:
                        self.inited = 2
                    elif self.userClient.mid is None:
                        self.inited = 4
                    else:
                        self.inited = 5
                    if self.db is not None:
                        with self.GetCursor() as cur:
                            cur.SetTextVar("oAMid", self.oAClient.mid)
        if self.inited == 2 and self.hasOA:
            while True:
                code = str(randint(1000, 9999))
                if code != self._1code:
                    self._1code = code
                    break
            self.inited = 3
            s = "[Init3] " + self._1code
            print("INIT3")
            if self.oAClient.obj is None:
                self.oAClient.obj = self.userClient._1GetObjByLineMid(self.oAClient.mid)
                self.userClient._2SendText(self.oAClient.mid, s)
            else:
                self.userClient._1SendText(self.oAClient.obj, s)
        if self.inited == 3 and event.chatroom.chatroomType == ChatroomType.user:
            print("INIT4a")
            if event.eventType == EventType.message and event.messageType == MessageType.text:
                print("INIT4b")
                mI3 = self._1init3Regex.match(event.text)
                if mI3 is not None and mI3.group(1) == self._1code:
                    print("INIT4c")
                    self.userClient.id = event.sender.id
                    self.userClient.obj = self.oAClient._1GetObjByLineId(self.userClient.id)
                    if self.userClient.mid is None:
                        self.inited = 4
                    else:
                        self.inited = 5
                    if self.db is not None:
                        print("INIT4d")
                        with self.GetCursor() as cur:
                            cur.SetTextVar("userId", self.userClient.id)
        if self.inited == 4 and event.chatroom.chatroomType == ChatroomType.group and event.eventType == EventType.message:
            #event.ReplyText("[Init4] Please kick me out and reinvite me later.")
            self.userClient._1SendText(event.chatroom, "[Init4] Please kick me out and reinvite me later.")
            
    def AddContinuousTextCommand(self, cmd):
        with Acquire(self.lock):
            self._1continuousTextCommands.append(cmd)
            self.hasContinuousTextCommands = True
            
    def HandleContinuousTextCommands(self, event):
        if self.hasContinuousTextCommands:
            args = {'continuous':CommandContinuousCallType.text, 'text':event.text, 'message':event, 'options':''}
            args = {'continuous':CommandContinuousCallType.text, 'text':event.text, 'message':event, 'options':''}
            ret = CommandResult.Failed()
            for cmd in self._1continuousTextCommands:
                ret = cmd.Call(msg=event, args=args)
                if ret.type == CommandResultType.done:
                    self.CommandDone(event.chatroom, ret, event=event)
                    return True
        return False
    
    def AddContinuousImageCommand(self, cmd):
        with Acquire(self.lock):
            self._1continuousImageCommands.append(cmd)
            self.hasContinuousImageCommands = True
    
    def AddContinuousAudioCommand(self, cmd):
        with Acquire(self.lock):
            self._1continuousAudioCommands.append(cmd)
            self.hasContinuousAudioCommands = True
    
    def AddContinuousVideoCommand(self, cmd):
        with Acquire(self.lock):
            self._1continuousVideoCommands.append(cmd)
            self.hasContinuousVideoCommands = True
    
    def AddContinuousFileCommand(self, cmd):
        with Acquire(self.lock):
            self._1continuousFileCommands.append(cmd)
            self.hasContinuousFileCommands = True
    
    def AddContinuousStickerCommand(self, cmd):
        with Acquire(self.lock):
            self._1continuousStickerCommands.append(cmd)
            self.hasContinuousStickerCommands = True
    
    def HandleContinuousImageCommands(self, event):
        if self.hasContinuousImageCommands:
            args = {'continuous':CommandContinuousCallType.image, 'images':[event.image], 'message':event, 'options':''}
            ret = CommandResult.Failed()
            for cmd in self._1continuousImageCommands:
                ret = cmd.Call(msg=event, args=args)
                if ret.type == CommandResultType.done:
                    self.CommandDone(event.chatroom, ret, event=event)
                    return True
            return False
    
    def HandleContinuousAudioCommands(self, event):
        if self.hasContinuousAudioCommands:
            args = {'continuous':CommandContinuousCallType.audio, 'audios':[event.audio], 'message':event, 'options':''}
            ret = CommandResult.Failed()
            for cmd in self._1continuousAudioCommands:
                ret = cmd.Call(msg=event, args=args)
                if ret.type == CommandResultType.done:
                    self.CommandDone(event.chatroom, ret, event=event)
                    return True
            return False
    
    def HandleContinuousFileCommands(self, event):
        if self.hasContinuousFileCommands:
            args = {'continuous':CommandContinuousCallType.file, 'files':[event.file], 'message':event, 'options':''}
            ret = CommandResult.Failed()
            for cmd in self._1continuousFileCommands:
                ret = cmd.Call(msg=event, args=args)
                if ret.type == CommandResultType.done:
                    self.CommandDone(event.chatroom, ret, event=event)
                    return True
            return False
    
    def HandleContinuousVideoCommands(self, event):
        if self.hasContinuousVideoCommands:
            args = {'continuous':CommandContinuousCallType.video, 'videos':[event.video], 'message':event, 'options':''}
            ret = CommandResult.Failed()
            for cmd in self._1continuousVideoCommands:
                ret = cmd.Call(msg=event, args=args)
                if ret.type == CommandResultType.done:
                    self.CommandDone(event.chatroom, ret, event=event)
                    return True
            return False
    
    def HandleContinuousStickerCommands(self, event):
        if self.hasContinuousStickerCommands:
            args = {'continuous':CommandContinuousCallType.sticker, 'message':event, 'options':''}
            ret = CommandResult.Failed()
            for cmd in self._1continuousStickerCommands:
                ret = cmd.Call(msg=event, args=args)
                if ret.type == CommandResultType.done:
                    self.CommandDone(event.chatroom, ret, event=event)
                    return True
            return False
    
    
    
    def HandleCommands(self, event, continuous = True):
        if event.eventType == EventType.message:
            if event.messageType == MessageType.content:
                if event.contentType == ContentType.IMAGE:
                    if not self.HandleImageCommands(event) and continuous:
                        return self.HandleContinuousImageCommands(event)
                elif event.contentType == ContentType.AUDIO:
                    return self.HandleContinuousAudioCommands(event)
                elif event.contentType == ContentType.VIDEO:
                    return self.HandleContinuousVideoCommands(event)
                elif event.contentType == ContentType.FILE:
                    return self.HandleContinuousFileCommands(event)
                elif event.contentType == ContentType.STICKER:
                    return self.HandleContinuousStickerCommands(event)
            elif event.messageType == MessageType.text:
                if event.text == '/commandlist' or event.text == '/commands':
                    event.ReplyText(self.commandList)
                    return True
                if Alphanumeric(event.text[:8])[0] == '/':
                    if self.HandleTextCommands(event):
                        return True
                if continuous:
                    return self.HandleContinuousTextCommands(event)
        return False
    
    def HandleImageCommands(self, event):
        chatroom = event.chatroom
        if chatroom not in self._1imageWaitingCommands:
            #print("chatroom not in _1imageWaitingCommands")
            return False
        sender = event.sender
        k = sender
        iWCchatroom = self._1imageWaitingCommands[chatroom]
        if sender in iWCchatroom:
            stack = iWCchatroom[sender]
        elif None in iWCchatroom:
            stack = iWCchatroom[None]
            k = None
        else:
            #print("sender not in _1imageWaitingCommands")
            return False
        try:
            ret = stack.CallImage(event)
            chatroom = event.chatroom
            sender = event.sender
            if ret.type != CommandResultType.expectImage:
                del self._1imageWaitingCommands[chatroom][k]
            if ret.type == CommandResultType.done:
                self.CommandDone(chatroom, ret, event=event)
            return True
        except Exception as e:
            if len(stack.stack) > 0:
                x = "(" + stack.stack[-1].cmd.name + ")"
            else:
                x = ""
            s = "[HandleImageCommands" + x + "] Unhandled Exception\n"
            self.Report(s+format_exc())
            event.ReplyText(s+str(e))
        return False
        
    
    _1commandRegex = compile("^([^ ]+)( ?)")
    
    @property
    def commandList(self):
        if self.hasCommands:
            l = sorted([x for x in self._1commands.items()])
            s = 'Commands :'
            for k, v in l:
                si = "\n%s" % k
                if k != v.name:
                    si = si + (" (%s)" % v.name)
                s = s + si
            return s
        return 'No command registered'
    
    @property
    def adminCommandList(self):
        if self.hasAdminCommands:
            l = sorted([x for x in self._1adminCommands.items()])
            s = 'Admin commands :'
            for k, v in l:
                si = "\n%s" % k
                if k != v.name:
                    si = si + (" (%s)" % v.name)
                s = s + si
            return s
        return 'No admin command registered'
                            
    def HandleTextCommands(self, event):
        alphanumericed = False
        name, x, text = event.text.partition(' ')
        name = name.strip()[1:]
        if name != 'admin' and name not in self._1commands:
            name, x, text = Alphanumeric(event.text).partition(' ')
            alphanumericed = True
            name = name.strip()[1:]
        cmd = None
        args = {'admin':False}
        if name == 'admin':
            if self.hasAdmins and self.hasAdminCommands and event.sender is not None and (event.sender in self.adminObjs or ((not IsEmpty(event.sender.id)) and event.sender.id in self.adminIds) or ((not IsEmpty(event.sender.mid)) and event.sender.mid in self.adminMids)):
                args['admin'] = True
                name = None
                name, x, text2 = event.text.partition(' ')
                name = name.strip()
                if name in self._1adminCommands:
                    text = text2
                elif not alphanumericed:
                    name, x, text = Alphanumeric(text.strip()).partition(' ')
                    name = name.strip()
                    alphanumericed = True
                if name in self._1adminCommands:
                    cmd = self._1adminCommands[name]
                else:
                    name = name.lower()
                    if name in self._1adminCommands:
                        cmd = self._1adminCommands[name]
        elif self.hasCommands:
            cmd = None
            if name in self._1commands:
                cmd = self._1commands[name]
            else:
                name = name.lower()
                if name in self._1commands:
                    cmd = self._1commands[name]
                else:
                    #print("COMMAND %s NOT FOUND" % name)
                    pass
        if cmd is not None:
            if cmd.escapeNames:
                text = EscapeNames(event.chatroom, event.sender, text)
            if cmd.Desc(event, text).type == CommandResultType.description:
                return True
            else:
                try:
                    stack = CommandStack(msg=event, baseArgs=args)
                    stack.Add(cmd=cmd, msg=event, args=cmd.ParseArgs(msg=event, text=text, stack=stack))
                    ret = stack.Call(event)
                    chatroom = event.chatroom
                    sender = event.sender
                    if ret.type == CommandResultType.expectImage:
                        if chatroom not in self._1imageWaitingCommands:
                            self._1imageWaitingCommands[chatroom] = {}
                        self._1imageWaitingCommands[chatroom][sender] = stack
                    else:
                        if chatroom in self._1imageWaitingCommands and sender in self._1imageWaitingCommands[chatroom]:
                            del self._1imageWaitingCommands[chatroom][sender]
                        if ret.type == CommandResultType.done:
                            self.CommandDone(event.chatroom, ret, event=event)
                    return True
                except Exception as e:
                    s = "[HandleTextCommands(" + name + ")] Unhandled Exception\n"
                    self.Report(s+format_exc())
                    event.ReplyText(s+str(e))
        return False
    
    
    def CommandDone(self, chatroom, ret, event=None):
        texts = ret.texts
        if isinstance(texts, str):
            chatroom.SendText(EscapeNames(chatroom, event.sender, texts), event=event)
        elif isinstance(texts, list):
            for x in texts:
                chatroom.SendText(EscapeNames(chatroom, event.sender, x), event=event)
        images = ret.images
        if isinstance(images, ImageMessage):
            chatroom.SendImage(images.image)
        elif isinstance(images, Image):
            chatroom.SendImage(images)
        elif isinstance(images, list):
            for x in images:
                chatroom.SendImage(x)
    
    def GetGroupName(self, group):
        if group.hasUser:
            return self.userClient._1GetGroupName(group)
    
    def GetMembers(self, room):
        if not room.hasUser:
            return room._1members
        if room.chatroomType == ChatroomType.room:
            return self.userClient._1GetRoomMembers(room)
        if room.chatroomType == ChatroomType.group:
            return self.userClient._1GetGroupMembers(room)
        raise Exception("[Client.GetMembers] 'room' is a User")
        
    def GetGroupInvitees(self, group):
        if group.chatroomType != ChatroomType.group:
            raise Exception("[Client.GetInvitees] 'group' is not a Group")
        return self.userClient._1GetGroupInvitees(group)
        
    
    def GetProfile(self, user):
        if isinstance(user, list):
            return [self.GetProfile(x) for x in user]
        if user.chatroomType != ChatroomType.user:
            raise Exception("[Client.GetProfile] 'user' is not User")
        if user.hasOA:
            try:
                self.oAClient._1GetProfile(user)
            except Exception as e:
                print_exc()
                raise
        if user.hasUser:
            try:
                self.userClient._1GetProfile(user)
            except Exception as e:
                print_exc()
                raise
        return user._1profile
    
    def Handle(self, event, thread = True):
        if self.inited < 5:
            self.Init2(event)
        if self.hasCommands or self.hasAdminCommands:
            if self.HandleCommands(event):
                return
        if self.handler is not None:
            if thread:
                self.Thread(self.handler, [event])
            else:
                self.handler(event)
        if self.oAAutoLeaveWhenUserLeave and event.eventType == EventType.left and event.receiver == Receiver.user:
            if thread:
                Timer(5, target=self.Thread, args=[event.chatroom.Leave, []]).start()
            else:
                event.chatroom.Leave()
    
    def HandleMany(self, events, thread=True):
        for e in events:
            self.Thread(self.Handle, [event, thread])
        
    def CreateDatabase(self, url):
        self.db = Database(self, url)
        with self.GetCursor() as cur:
            cur.Execute('CREATE TABLE IF NOT EXISTS TextVars(name TEXT UNIQUE, value TEXT)')
            cur.Execute('CREATE TABLE IF NOT EXISTS ChatRooms(id SERIAL PRIMARY KEY, lineId TEXT UNIQUE, lineMid TEXT UNIQUE, type INTEGER, hasOA BOOLEAN DEFAULT FALSE, hasUser BOOLEAN DEFAULT FALSE, uId INTEGER)')
            cur.Execute('CREATE TABLE IF NOT EXISTS Users(id SERIAL PRIMARY KEY, lineId TEXT UNIQUE, lineMid TEXT UNIQUE, rId INTEGER, dummy BOOLEAN)')
            cur.Execute('CREATE TABLE IF NOT EXISTS LineIdByMsgId(msgId TEXT UNIQUE, lineId TEXT)')
            cur.Execute('CREATE TABLE IF NOT EXISTS LineMidByMsgId(msgId TEXT UNIQUE, lineMid TEXT)')
            cur.Execute('CREATE TABLE IF NOT EXISTS SenderLineIdByMsgId(msgId TEXT UNIQUE, lineId TEXT)')
            cur.Execute('CREATE TABLE IF NOT EXISTS SenderLineMidByMsgId(msgId TEXT UNIQUE, lineMid TEXT)')
            cur.SetTextVar('dbUrl', url)
            cur.Commit()
        return self.db
    
    def SendText(self, to, text, event=None):
        if type(text) is list:
            ret = True
            for t in text:
                ret = ret and self.SendText(to, t)
            return ret
        if not isinstance(to, list):
            sender = None
            msgId = None
            receiver = Receiver.none
            if event is not None:
                receiver = event.receiver
                if event.eventType == EventType.message:
                    msgId = event.id
                    sender = event.sender
            elif to.hasOA:
                sender = self.oAClient.obj
            elif to.hasUser:
                sender = self.userClient.obj
            msg = self._1TextMessage(msgId, text, to, receiver, sender=sender)
            if self.HandleCommands(msg, continuous = False):
                return
        return self._1SendText(to, text)
    
    def _1SendText(self, to, text):
        text = Clean(text)
        if isinstance(to, list):
            toa = []
            tob = []
            for t in to:
                if t.hasOA:
                    toa.append(t)
                elif t.hasUser:
                    tob.append(t)
            ret = True
            e = ''
            if len(toa) > 0:
                try:
                    ret = ret and self.oAClient._1SendText(toa, text)
                except Exception as ex:
                    for t in toa:
                        if t.hasUser:
                            tob.append(t)
                    print_exc()
                    if len(tob) < len(to):
                        e = "Message '" + text + "' not sent to " + str([x for x in to if x not in tob]) + "\n"
                    e = e + "[Client._1SendText:list:OA]\n" + format_exc()
            try:
                ret = ret and self.userClient._1SendText(tob, text)
            except Exception as ex:
                print_exc()
                e = e + '\n[Client._1SendText:list:User]\n' + format_exc()
            if IsEmpty(e):
                return ret
            else:
                raise Exception(e)
        e = ''
        if to.hasOA:
            try:
                return self.oAClient._1SendText(to, text)
            except Exception as ex:
                
                e = e + ("[Client._1SendText:single:OA]\nto=%s\nhasOA=%s\n_1hasOA=%s\n_2hasOA=%s\nid=%s\n" % (str(to), str(to.hasOA), str(to._1hasOA), str(to._2hasOA), str(to.id))) + format_exc()
        if to.hasUser:
            try:
                ret = self.userClient._1SendText(to, text)
                if not IsEmpty(e):
                    self.Report(e)
                return ret
            except Exception as ex:
                e = e + '\n[Client._1SendText:single:User]\n' + format_exc()
        if IsEmpty(e):
            raise Exception("UNKNOWN ERROR \nto=%s\nhasOA=\n%s\nhasUser=%s\nlineId=%s\nlineMid=%s\nclientHasOA=%s\nclientHasUser=%s\n_1hasUser=%s\n_2hasUser=%s\n_1hasOA=%s\n_2hasOA=%s" % (str(to), str(to.hasOA), str(to.hasUser), str(to.id), str(to.mid), str(self.hasOA), str(self.hasUser), str(to._1hasUser), str(to._2hasUser), str(to._1hasOA), str(to._2hasOA)))
        raise Exception(e)
        
    def SendTextOA(self, to, text, event=None):
        text = text.decode('utf-8', 'ignore').encode('utf-8')
        if isinstance(text, list):
            ret = True
            for x in text:
                ret = ret and self.SendTextOA(to, text, event)
            return ret
        return self.oAClient._1SendText(to, text)
        
    def SendTextUser(self, to, text, event=None):
        text = text.decode('utf-8', 'ignore').encode('utf-8')
        if isinstance(text, list):
            ret = True
            for x in text:
                ret = ret and self.SendTextUser(to, text, event)
            return ret
        return self.userClient._1SendText(to, text)
        
    def AddCommand(self, cmd, name=None):
        if not name:
            name = cmd.name
        self._1commands[name] = cmd
        self.hasCommands = True
        if cmd.initFunction is not None:
            cmd.initFunction(client=self)
        
    def AddAdminCommand(self, cmd, name=None):
        if not self.hasAdmins:
            raise Exception("[Client.AddAdminCommand] This client doesn't have any admins specified")
        if not name:
            name = cmd.name
        self._1adminCommands[name] = cmd
        self.hasAdminCommands = True
        if cmd.initFunction is not None:
            cmd.initFunction(client=self)
        
    def SendImageWithBytes(self, to, bytes):
        if type(bytes) is list:
            ret = True
            for b in b:
                ret = ret and self.SendImageWithBytes(to, b)
            return ret
        return self._1SendImageWithBytes(to, bytes)
    
    def _1SendImageWithBytes(self, to, bytes):
        if isinstance(to, list):
            toa = []
            tob = []
            for t in to:
                if t.hasUser:
                    toa.append(t)
                elif t.hasOA:
                    tob.append(t)
            ret = True
            e = ''
            if len(toa) > 0:
                try:
                    ret = ret and self.userClient._1SendImageWithBytes(toa, bytes)
                except Exception as ex:
                    for t in toa:
                        if t.hasUser:
                            tob.append(t)
                    if len(tob) < len(to):
                        e = "Image '" + url + "' not sent to " + str([x for x in to if x not in tob]) + "\n"
                    e = e + "[Client._1SendImage:list:User]\n" + format_exc()
            if len(tob) > 0:
                if self.pyImgurKey is None:
                    raise Exception("[Client._1SendImage:list:OA:1] Must have 'pyImgurKey' set")
                try:
                    ret = ret and self.oAClient._1SendImageWithBytes(tob, bytes)
                except Exception as ex:
                    e = e + '\n[Client._1SendImage:list:OA]\n' + format_exc()
                if IsEmpty(e):
                    return ret
                else:
                    raise Exception(e)
        e = ''
        if to.hasUser:
            try:
                return self.userClient._1SendImageWithBytes(to, bytes)
            except Exception as ex:
                s = format_exc()
                #print(s)
                e = e + '\n[Client._1SendImage:single:User]\n' + s
        if to.hasOA:
            if self.pyImgurKey is None:
                s = "[Client._1SendImage:single:OA:1] Must have 'pyImgurKey' set"
                if IsEmpty(e):
                    raise Exception(s)
                else:
                    e = e + s
            try:
                ret = self.oAClient._1SendImageWithBytes(to, bytes)
                if not IsEmpty(e):
                    self.Report(e)
                return ret
            except Exception as ex:
                e = e + "[Client._1SendImage:single:OA]\n" + format_exc()
        raise Exception(e)
        
    def SendImage(self, to, image):
        if isinstance(image, ImageMessage):
            image = image.images
        if isinstance(image, list):
            ret = True
            for x in image:
                ret = ret and self.SendImage(x.bytes)
            return ret
        return self.SendImageWithBytes(to, image.bytes)
        
    def SendImageWithUrl(self, to, url):
        if type(url) is list:
            ret = True
            for u in url:
                ret = ret and self.SendImageWithUrl(to, u)
            return ret
        return self._1SendImageWithUrl(to, url)
        
    def _1SendImageWithUrl(self, to, url):
        if isinstance(to, list):
            toa = []
            tob = []
            for t in to:
                if t.hasUser:
                    toa.append(t)
                elif t.hasOA:
                    tob.append(t)
            ret = True
            e = ''
            if len(toa) > 0:
                try:
                    ret = ret and self.userClient._1SendImageWithUrl(toa, url)
                except Exception as ex:
                    for t in toa:
                        if t.hasUser:
                            tob.append(t)
                    if len(tob) < len(to):
                        e = "Image '" + url + "' not sent to " + str([x for x in to if x not in tob]) + "\n"
                    e = e + "[Client._1SendImageWithUrl:list:User]\n" + format_exc()
            if len(tob) > 0:
                try:
                    ret = ret and self.oAClient._1SendImageWithUrl(tob, url)
                except Exception as ex:
                    e = e + '\n[Client._1SendImageWithUrl:list:OA]\n' + format_exc()
                if IsEmpty(e):
                    return ret
                else:
                    raise Exception(e)
        e = ''
        if to.hasUser:
            try:
                return self.userClient._1SendImageWithUrl(to, url)
            except Exception as ex:
                e = e + '\n[Client._1SendImageWithUrl:single:User]\n' + format_exc()
        if to.hasOA:
            try:
                ret = self.oAClient._1SendImageWithUrl(to, url)
                if not IsEmpty(e):
                    self.Report(e)
                return ret
            except Exception as ex:
                e = e + "[Client._1SendImageWithUrl:single:OA]\n" + format_exc()
        raise Exception(e)
    
    def SendButtons(self, to, buttons):
        if isinstance(to, list):
            for t in to:
                if not t.hasOA:
                    if isinstance(t, Room) and t.uId:
                        t.InitRole(True)
                    raise Exception("[Client.SendButtons:list] No OAClient")
        elif not to.hasOA:
            if isinstance(to, Room) and tp.uId:
                to.InitRole(True)
            raise Exception("[Client.SendButtons:single] No OAClient") 
        return self.oAClient._1SendButtons(to, buttons)
        
            
    def Report(self, msg = None):
        if msg is None:
            msg = format_exc()
        msg = "[Report] " + msg
        print(msg)
        ex = ''
        if len(self.adminObjs) > 0:
            try:
                return self.adminObjs[0].SendText(msg)
            except Exception as e:
                ex = ex + "\n[Client.Report.Obj]\n" + format_exc()
        if self.hasOA and len(self.adminIds) > 0:
            try:
                return self.oAClient._1Report(msg)
            except Exception as e:
                ex = ex + "\n[Client.Report.OA]\n" + format_exc()
        if self.hasUser and len(self.adminMids) > 0:
            try:
                return self.userClient._1Report(msg)
            except Exception as e:
                ex = ex + "\n[Client.Report.User]\n" + format_exc()
        raise Exception(ex)
        
    def AddUser(self, user):
        if isinstance(user, list):
            return self.AddUsers(user)
        if not user.hasUser:
            return False
        if user._1profile.status == UserStatuses.friend:
            return True
        return self.userClient._1AddUser(user)
        
    def AddUsers(self, users):
        users = [x for x in users if x._1profile.status == UserStatuses.friend]
        return self.userClient._1AddUsers(users)
    
    def CreateGroup(self, name="No Name", users=[]):
        if not isinstance(users, list):
            users = [users]
        if len(users) == 0:
            return False
        noUsers = [x for x in users if not x.hasUser]
        l = len(noUsers) 
        if l > 0:
            if l == len(users):
                return False
            raise Exception("[Client.CreateGroup] hasUser is False on some of the users\n" + str(noUsers))
        return self.userClient._1CreateGroup(name, users)
    
    def CreateRoom(self, users):
        if not isinstance(users, list):
            users = [users]
        noUsers = [x for x in users if not x.hasUser]
        l = len(noUsers) 
        if l > 0:
            if l == len(users):
                return False
            raise Exception("[Client.CreateRoom] hasUser is False on some of the users\n" + str(noUsers))
        return self.userClient._1CreateRoom(users)
    
    def InviteInto(self, room, users):
        if not isinstance(users, list):
            users = [users]
        noUsers = [x for x in users if not x.hasUser]
        l = len(noUsers) 
        if l > 0:
            if l == len(users):
                return False
            raise Exception("[Client.InviteInto] hasUser is False on some of the users\n" + str(noUsers))
        return self.userClient._1InviteInto(room, users)
    
    def Leave(self, room):
        if room.chatroomType == ChatroomType.user:
            raise Exception("[Client.Leave] 'room' is a User")
        ret = True
        if room.hasUser:
            ret = ret and self.userClient._1Leave(room)
        if room.hasOA:
            ret = ret and self.oAClient._1Leave(room)
        return ret
    
    def JoinGroup(self, group):
        if not group.hasUser:
            return False
        return self.userClient._1JoinGroup(group)
    
    def KickFromGroup(self, group, users):
        if not isinstance(users, list):
            users = [users]
        if not group.hasUser:
            return False
        noUsers = [x for x in users if not x.hasUser]
        l = len(noUsers) 
        if l > 0:
            if l == len(users):
                return False
            raise Exception("[Client.KickFromGroup] hasUser is False on some of the users\n" + str(noUsers))
        return self.userClient._1KickFromGroup(group, users)
        
        
        
        
    def ReportAll(self, msg):
        if msg is None:
            msg = format_exc()
        msg = "[Report] " + msg
        print(msg)
        ex = ''
        if len(self.adminObjs) > 0:
            try:
                return self.SendText(self.adminObjs, msg)
            except Exception as e:
                s = "[Client.ReportAll.Obj]\n" + format_exc()
                print(s)
                ex = ex + "\n" + s
        if self.hasOA:
            try:
                return self.oAClient._1ReportAll(msg)
            except Exception as e:
                s = "[Client.ReportAll.OA]\n" + format_exc()
                print(s)
                ex = ex + "\n" + s
        if self.hasUser:
            try:
                return self.userClient._1ReportAll(msg)
            except Exception as e:
                s = "[Client.ReportAll.User]\n" + format_exc()
                print(s)
                ex = ex + "\n" + s
        raise Exception(ex)
        
    def _1Update(self, chatroom, receiver):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return Update(self, chatroom, receiver)
        
    def _1TextMessage(self, id, text, chatroom, receiver, sender = None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return TextMessage(self, id, text, chatroom, receiver, sender=sender)
        
    def _1StickerMessage(self, id, packageId, stickerId, chatroom, receiver, sender = None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return StickerMessage(self, id, packageId, stickerId, chatroom, receiver, sender=sender)
        
    def _1ContactMessage(self, id, displayName, mid, chatroom, receiver, sender = None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return ContactMessage(self, id, displayName, mid, chatroom, receiver, sender=sender)
        
    def _1LocationMessage(self, id, title, address, latitude, longitude, chatroom, receiver, sender = None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return LocationMessage(self, id, title, address, latitude, longitude, chatroom, receiver, sender=sender)
    
    def _1ImageMessage(self, id, chatroom, receiver, sender = None, url=None, bytes=None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return ImageMessage(self, id, chatroom, receiver, sender=sender, url=url, bytes=bytes)
    
    def _1AudioMessage(self, id, chatroom, receiver, sender = None, url=None, bytes=None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return AudioMessage(self, id, chatroom, receiver, sender=sender, url=url, bytes=bytes)
    
    def _1VideoMessage(self, id, chatroom, receiver, sender = None, url=None, bytes=None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return VideoMessage(self, id, chatroom, receiver, sender=sender, url=url, bytes=bytes)
    
    def _1FileMessage(self, id, chatroom, receiver, sender = None, url=None, bytes=None):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return FileMessage(self, id, chatroom, receiver, sender=sender, url=url, bytes=bytes)
    
    def _1Unfollowed(self, chatroom, receiver):
        if receiver == Receiver.oA:
            chatroom.hasOA = False
        elif receiver == Receiver.user:
            chatroom.hasUser = False
        return Unfollowed(self, chatroom, receiver)
    
    def _1Followed(self, chatroom, receiver):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        return Followed(self, chatroom, receiver)

    def _1Joined(self, chatroom, receiver):
        if receiver == Receiver.oA:
            chatroom.hasOA = True
        elif receiver == Receiver.user:
            chatroom.hasUser = True
        chatroom.InitRoom(False)
        return Joined(self, chatroom, receiver)
        
    def _1Left(self, chatroom, receiver):
        if receiver == Receiver.oA:
            chatroom.hasOA = False
        elif receiver == Receiver.user:
            chatroom.hasUser = False
        return Left(self, chatroom, receiver)
    
    def _1Invited(self, chatroom, receiver):
        if receiver == Receiver.oA:
            chatroom.hasOA = False
        elif receiver == Receiver.user:
            chatroom.hasUser = False
        return Invited(self, chatroom, receiver)
    
    def StartOA(self, thread=True, port=None):
        if port is None:
            port = self.port
        else:
            self.port = port
        if self.oAClient:
            if not self.userClient:
                self.started = True
            self.oAClient.Start(thread=thread, port=port)
            return True
        return False
            
            
    def StartUser(self, thread=0, mode=None):
        if self.userClient:
            self.userClient.Start(thread=thread, mode=mode)
            return True
        return False
    
    def StartMain(self, thread=True, main=1, timeout=1):
        if main<1:
            return False
        if thread:
            self.Thread(self.Main, [main, timeout])
        else:
            self.Main(main, timeout)
        return True
        
    def AddEvent(self, event, force=False):
        if isinstance(event, Message):
            id = event.id
            with self.mLock:
                if force or id not in self.messages:
                    self.messages[id] = event
                    self.eventQueue.append(id)
        else:
            self.eventQueue.append(event)
        with self.eCond:
            self.eCond.notifyAll()
                
    def Main(self, main=1, timeout=1):
        self.main = main
        while True:
            e = None
            with self.eCond:
                while not e:
                    try:
                        e = self.eventQueue.pop(0)
                    except IndexError:
                        self.eCond.wait(1)
            if not isinstance(e, Event):
                with self.mLock:
                    e = self.messages.pop(e, None)
                    if not e:
                        continue
            try:
                if main == 1:
                    self.Handle(e, False)
                else:
                    t = self.Thread(self.Handle, [e, False])
                    if main == 2:
                        t.join(timeout)
            except Exception as ex:
                self.Report(format_exc())
        self.main = 0
            
            
            
        