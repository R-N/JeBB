import ssl



try:
    _create_unverified_https_context = ssl._1create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._1create_default_https_context = _create_unverified_https_context



from traceback import format_exc, print_exc, print_stack
from tempfile import gettempdir
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage as _TextMessage, TextSendMessage, TemplateSendMessage, TemplateAction, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, ButtonsTemplate, PostbackEvent, CarouselTemplate, CarouselColumn, LeaveEvent, FollowEvent, UnfollowEvent, JoinEvent, ImageSendMessage, ImageMessage as _ImageMessage

from .api.line_0_10_0.ttypes import TalkException, MIDType, OpType, IdentityProvider, Message as _Message, ContentType
from requests.exceptions import (ReadTimeout, Timeout)

from .api.api import LineAPI, needAuthErrors, validContentTypes
from .models.types import Receiver, MessageType, ChatroomType, EventType, UserStatus, UserRelation, WhenOALeave
from .models.events import Joined, Invited, Left, Followed, Unfollowed, Message, TextMessage, ImageMessage, Update, Button, Buttons
from .models.chatrooms import User, Room, Group
from .models.database import Database
from .models.command import defaultParameter
from .utils import IsEmpty, emailRegex, Lock, Alphanumeric, FormatStack, Acquire

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
    
def CheckAuth(func):
    def WrapperCheckAuth(*args, **kwargs):
        if args[0]._1CheckAuth():
            return func(*args, **kwargs)
    return WrapperCheckAuth
    
class UserClient(object):
    loginVersion = "4.1.3.586"
    version = "5.2.2.1459"
    def __init__(self, client, mode=1):
        self.lock = Lock()
        with Acquire(self.lock, client.lock):
            self.client = client
        with Acquire(self.lock):
            self.authTimer = self.reauthDelay
            self.thread = None
            self.thread2 = None
            self._1running = False
            self._1ready = False
            self.adminObjs = []
            self.obj = None
            self.midLocks = {}
            self.opsCond = Condition()
            self.mode = mode
            self.ops = []
            self.lastPing = time()
            self._1shouldPing = False
            self.timeUnpinged = 0
            self._1client = self._1GetClient()

    @property
    def shouldPing(self):
        return self._1shouldPing

    @shouldPing.setter
    def shouldPing(self, value):
        if value and self.timeUnpinged > 300:
                RequestsGet(self.pingAddress)
                self.timeUnpinged = 0
        self._1shouldPing = value


    @property
    def pingInterval(self):
        return self.client.pingInterval

    @property
    def pingAddress(self):
        if self.client.hasOA:
            return self.client.pingAddress
            
    @property
    def name(self):
        return self.client.userName
            
    @property
    def opsLen(self):
        return len(self.ops)
            
    @property
    def _1headers(self):
        return self.client._1headers
    
    @_1headers.setter
    def _1headers(self, value):
        self.client._1headers = value
            
    @property
    def comName(self):
        return self.client.comName
    
    @comName.setter
    def comName(self, value):
        self.client.comName = value
            
    @property
    def obj(self):
        return self.client.userObj
    
    @obj.setter
    def obj(self, value):
        self.client.userObj = value
            
    @property
    def mid(self):
        return self.client.userMid
    
    @mid.setter
    def mid(self, value):
        self.client.userMid = value
            
    @property
    def id(self):
        return self.client.userId
    
    @id.setter
    def id(self, value):
        self.client.userId = value
            
    @property
    def autoAcceptInvitation(self):
        return self.client.autoAcceptInvitation
    
    @autoAcceptInvitation.setter
    def autoAcceptInvitation(self, value):
        self.client.autoAcceptInvitation = value
            
    @property
    def whenOALeave(self):
        return self.client.whenOALeave
    
    @whenOALeave.setter
    def whenOALeave(self, value):
        self.client.whenOALeave = value
            
    @property
    def adminMids(self):
        return self.client.adminMids
    
    @adminMids.setter
    def adminMids(self, value):
        self.client.adminMids = value
            
    @property
    def tries(self):
        return self.client.tries
    
    @tries.setter
    def tries(self, value):
        self.client.tries = value
            
    @property
    def reauthDelay(self):
        return self.client.reauthDelay
    
    @reauthDelay.setter
    def reauthDelay(self, value):
        self.client.reauthDelay = value
            
    @property
    def isMac(self):
        return self.client.isMac
    
    @isMac.setter
    def isMac(self, value):
        self.client.isMac = value
            
    @property
    def certificate(self):
        return self.client.certificate
    
    @certificate.setter
    def certificate(self, value):
        print("SETTING certificate TO " + str(value))
        self.client.certificate = value
            
    @property
    def authToken(self):
        return self.client.authToken
    
    @authToken.setter
    def authToken(self, value):
        print("SETTING authToken TO " + str(value))
        self._1headers["X-LINE-ACCESS"] = value
        self.client.authToken = value
            
    @property
    def password(self):
        return self.client.password
    
    @password.setter
    def password(self, value):
        self.client.password = value
            
    @property
    def email(self):
        return self.client.email
    
    @email.setter
    def email(self, value):
        self.client.email = value
            
    
    def _1Update(self, chatroom):
        chatroom.hasUser = True
        return self.client._1Update(chatroom, Receiver.user)
            
    def _1TextMessage(self, id, text, chatroom, sender = None):
        chatroom.hasUser = True
        return self.client._1TextMessage(id, text, chatroom, Receiver.user, sender=sender)
    
    def _1StickerMessage(self, id, packageId, stickerId, chatroom, sender = None):
        chatroom.hasUser = True
        return self.client._1StickerMessage(id, packageId, stickerId, chatroom, Receiver.user, sender=sender)
    
    def _1ContactMessage(self, id, displayName, mid, chatroom, sender = None):
        chatroom.hasUser = True
        return self.client._1ContactMessage(id, displayName, mid, chatroom, Receiver.user, sender=sender)
    
    def _1LocationMessage(self, id, title, address, latitude, longitude, chatroom, sender = None):
        chatroom.hasUser = True
        return self.client._1LocationMessage(id, title, address, latitude, longitude, chatroom, Receiver.user, sender=sender)
    
    def _1ImageMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasUser = True
        return self.client._1ImageMessage(id, chatroom, Receiver.user, sender=sender, url=url, bytes=bytes)
    
    def _1AudioMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasUser = True
        return self.client._1AudioMessage(id, chatroom, Receiver.user, sender=sender, url=url, bytes=bytes)
    
    def _1VideoMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasUser = True
        return self.client._1VideoMessage(id, chatroom, Receiver.user, sender=sender, url=url, bytes=bytes)
    
    def _1FileMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasUser = True
        return self.client._1FileMessage(id, chatroom, Receiver.user, sender=sender, url=url, bytes=bytes)
    
    def _1Unfollowed(self, chatroom):
        chatroom.hasUser = False
        return self.client._1Unfollowed(chatroom, Receiver.user)
    
    def _1Followed(self, chatroom):
        chatroom.hasUser = True
        return self.client._1Followed(chatroom, Receiver.user)

    def _1Joined(self, chatroom):
        chatroom.hasUser = True
        return self.client._1Joined(chatroom, Receiver.user)
        
    def _1Left(self, chatroom):
        chatroom.hasUser = False
        return self.client._1Left(chatroom, Receiver.user)
    
    def _1Invited(self, chatroom):
        chatroom.hasUser = False
        return self.client._1Invited( chatroom, Receiver.user)
            
    def _1JoinGroup(self, group):
        if group.chatroomType != ChatroomType.group:
            raise Exception("[UserClient._1JoinGroup] Object is not a Group")
        return self._2JoinGroup(group.mid)
    
    def _1Try(self, method, args=[], kwargs={}):
        for i in range(0, self.tries):
            try:
                return method(*args, **kwargs)
            except TalkException as e:
                print_exc()
                raise
            except Exception as e:
                print_exc()
                pass
                raise
    
        
    def _2JoinGroup(self, mid):
        return self._1Try(self._1client._1acceptGroupInvitation, [mid])
        
    def _1Leave(self, room):
        if room.chatroomType == ChatroomType.user:
            raise Exception("[UserClient._1Leave] Object is a User")
        if room.uObj:
            room.RemoveLink()
        if not room.hasUser:
            return False
        if room.chatroomType == ChatroomType.group:
            return self._2LeaveGroup(room.mid)
        return self._2LeaveRoom(room.mid)
    
    def _2LeaveGroup(self, mid):
        if room.uObj:
            room.RemoveLink()
        return self._1Try(self._1client._1leaveGroup, [mid])
        
    def _2LeaveRoom(self, mid):
        if room.uObj:
            room.RemoveLink()
        return self._1Try(self._1client._1leaveRoom, [mid])
        
    def _1InviteInto(self, room, users = []):
        if room.chatroomType == ChatroomType.user:
            raise Exception("[UserClient._1InviteInto:1] 'Room' is a User")
        nonUsers = [x for x in users if x.chatroomType != ChatroomType.user]
        if len(nonUsers) > 0:
            raise Exception("[UserClient._1InviteInto:2] Some of the 'users' aren't Users\n" + str(nonUsers))
        if room.chatroomType == ChatroomType.room:
            return self._2InviteIntoRoom(room.mid, [x.mid for x in users])
        return self._2InviteIntoGroup(room.mid, [x.mid for x in users])
    
    def _1RefreshAll(self):
        try:
            print("REFRESHALL")
            self._1GetAllGroups()
            self._1GetAllUsers()
            self._1GetAllActiveRooms()
            print("REFRESHALL DONE")
            return True
        except Exception:
            print_exc()
            pass
        return False
    
    def _1GetAllUsers(self):
        objs = self._2GetAllUsers()
        users = [self._1GetObjByLineMid(x.id, obj=x) for x in objs]
        return users
    
    def _2GetAllUsers(self):
        return self._1Try(self._1getContacts, [self._2GetAllUserMids()])
    
    def _2GetAllUserMids(self):
        return self._1Try(self._1getAllContactIds)
        
    
    def _1GetAllActiveRooms(self, count=50):
        objs = self._2GetAllActiveRooms(count)
        rooms = [self._1GetObjByLineMid(x.id, obj=x) for x in objs]
        return rooms
    
    def _2GetAllActiveRooms(self, count=50):
        start = 1

        rooms = []

        while True:
            channel = self._1Try(self._1client._1getMessageBoxCompactWrapUpList, [start, count])
            #channel = self._1client._1getMessageBoxCompactWrapUpList(start, count)
            for box in channel.messageBoxWrapUpList:
                if box.messageBox.midType == MIDType.ROOM:
                    room = self._2GetRoom(box.messageBox.id)
                    rooms.append(room)
                else:
                    print("MIDTYPE %s" % MIDType._VALUES_TO_NAMES[box.messageBox.midType])

            if len(channel.messageBoxWrapUpList) == count:
                start += count
            else:
                break
        return rooms
        
        
    def _2InviteIntoRoom(self, mid, userMids = []):
        return self._1Try(self._1client._1inviteIntoRoom, [mid, userMids])
    
    def _2InviteIntoGroup(self, mid, userMids = []):
        return self._1Try(self._1client._1inviteIntoGroup, [mid, userMids])
        
    def _1CreateGroup(self, name = "No name", users = []):
        if IsEmpty(name):
            raise ("[UserClient._1CreateGroup:1] Name can't be empty")
        if len(users) < 1:
            raise ("[UserClient._1CreateGroup:2] Need at least 1 user")
        nonUsers = [x for x in users if x.chatroomType != ChatroomType.user]
        if len(nonUsers) > 0:
            raise Exception("[UserClient._1CreateGroup:3] Some of the 'users' aren't Users\n" + str(nonUsers))
        group0 = self._2CreateGroup(name, [x.mid for x in users])
        if group0 is None:
            return
        group = self._1GetObjByLineMid(group0.id, obj = group0)
        group.hasUser = True
        if self.client.hasOA and self.client.oAClient.obj and self.client.oAClient.obj in users:
            group.hasOA = True
        return group
    
    def _2CreateGroup(self, name = "No name", userMids=[]):
        return self._1Try(self._1client._1createGroup, [name, userMids])
    
    def _1GetAllGroups(self):
        return self._1GetAllGroupsInvited() + self._1GetAllGroupsJoined()
    
    def _2GetAllGroupsJoined(self):
        return self._2GetGroups(self._2GetAllGroupMidsJoined())
        
    def _2GetAllGroupsInvited(self):
        return self._2GetGroups(self._2GetAllGroupMidsInvited())
    
    def _1GetAllGroupsJoined(self):
        objs = self._2GetAllGroupsJoined()
        groups = [self._1GetObjByLineMid(x.id, obj=x) for x in objs]
        return groups
    
    def _1GetAllGroupsInvited(self):
        objs = self._2GetAllGroupsInvited()
        groups = [self._1GetObjByLineMid(x.id, obj=x, hasUser=False) for x in objs]
        if self.autoAcceptInvitation:
            for group in groups:
                group.hasUser = False
                group.Join()
        else:
            for group in groups:
                group.hasUser = False
            msgs = [self._1Invited(chatroom=group) for group in groups]
            self.client.HandleMany(msgs)
            for msg in msgs:
                if self.client.main:
                    self.client.AddEvent(msg)
                else:
                    self.client.Thread(self.client.Handle, [msg, False])
        return groups
        
    
    def _2GetAllGroupMidsJoined(self):
        return self._1Try(self._1client._1getGroupIdsJoined)
    
    def _2GetAllGroupMidsInvited(self):
        return self._1Try(self._1client._1getGroupIdsInvited)
    
        
    def _1CreateRoom(self, users = []):
        if len(users) < 1:
            raise ("[UserClient._1CreateRoom:1] Need at least 1 user")
        nonUsers = [x for x in users if x.chatroomType != ChatroomType.user]
        if len(nonUsers) > 0:
            raise Exception("[UserClient._1CreateRoom:2] Some of the 'users' aren't Users\n" + str(nonUsers))
        room0 = self._2CreateRoom([x.mid for x in users])
        if room0 is None:
            return
        room = self._1GetObjByLineMid(room0.mid, obj = room0)
        with Acquire(self.client.lock):
            room.hasUser = True
            if self.client.hasOA and self.client.oAClient.obj and self.client.oAClient.obj in users:
                room.hasOA = True
            room.InitRoom(True)
        return room
    
    def _2CreateRoom(self, userMids=[]):
        return self._1Try(self._1client._1createRoom, [userMids])
            
    def _1KickFromGroup(self, group, users=[]):
        if group.chatroomType == ChatroomType.user:
            raise Exception("[UserClient._1KickFromGroup:1] 'group' is not a Group")
        nonUsers = [x for x in users if x.chatroomType != ChatroomType.user]
        if len(nonUsers) > 0:
            raise Exception("[UserClient._1KickFromGroup:2] Some of the 'users' aren't Users\n" + str(nonUsers))
        return self._2KickFromGroup(group.mid, [x.mid for x in users])
    
    def _2KickFromGroup(self, mid, userMids):
        return self._1Try(self._1client._1kickoutFromGroup, [mid, userMids])
        
    def _1AddUser(self, user):
        return self._1AddUsers([user])
            
    def _1AddUsers(self, users):
        nonUsers = [x for x in users if x.chatroomType != ChatroomType.user]
        if len(nonUsers) > 0:
            raise Exception("[UserClient._1Add:1] Some of the following users are not users : " + str(nonUsers))
        dontHaveUsers = [x for x in users if not x.hasUser]
        if len(dontHaveUsers) > 0:
            raise Exception("[UserClient._1Add:1] Some of the following users do not hasUser : " + str(dontHaveUsers))
        objs = self._2AddUsers([x.mid for x in users])
        t = time()
        for i in range(0, len(objs)):
            users[i]._1SetObjAndTime(objs[i], t)
        return True
    
    def _2AddUsers(self, mids):
        return self._1Try(self._1client._1findAndAddContactsByMid, [mids])
    
    def _1GetRoomMembers(self, room):
        try:
            room0 = self._1client._1getRoom(room.mid) 
            room._1SetObjAndTime(room0)
        except Exception:
            room.time = time()
            pass
        return room._1members
    
    def _1GetProfile(self, user):
        if not user.hasUser:
            return
        try:
            user0 = self._1GetUsers([user])[0]
            user._1SetObjAndTime(user0)
        except TypeError:
            pass
        except Exception:
            self.client.Report(format_exc())
            user._1profile.time = time()
            pass
        return user._1profile
    
    def _1GetUsers(self, users):
        return self._2GetUsers([x.mid for x in users])
    
    def _2GetUsers(self, mids):
        return self._1Try(self._1client._1getContacts, [mids])
    
    def _1GetGroups(self, groups):
        try:
            groups0 = self._2GetGroups([x.mid for x in groups])
            if groups0:
                for i in range(0, len(groups0)):
                    groups[i]._1SetObjAndTime(groups0[i])
            return groups0
        except Exception:
            self.client.Report(format_exc())
            t = time()
            for x in groups:
                groups.time = t
            
    
    def _2GetGroups(self, mids):
        return self._1Try(self._1client._1getGroups, [mids])
    
    def _1GetGroupName(self, group):
        try:
            self._1GetGroups([group])
        except Exception:
            pass
        return group._1name
    
    def _1GetGroupMembers(self, group):
        try:
            self._1GetGroups([group])
        except Exception:
            pass
        return group._1members
    
    def _1GetGroupInvitees(self, group):
        try:
            self._1GetGroups([group])
        except Exception:
            pass
        return group._1invitees
    
    @property
    def ready(self):
        return self._1client is not None
    
    @ready.setter
    def ready(self,value):
        self._1ready = value
               
    @property
    def running(self):
        return self._1running and self._1client is not None 
    
    @running.setter
    def running(self, value):
        self._1running = value
    
    def _1CheckAuth(self):
        """Check if client is logged in or not"""
        if self.authToken:
            return True
        else:
            raise Exception("you need to login")
            
    
    def _1GetClientAuthToken(self, _client=None, authToken=None):
        with Acquire(self.lock):
            self._1ready = False
            if authToken is None:
                authToken = self.authToken
            print("E")
            if authToken is None:
                return None
            print("F")
            if _client is None:
                _client = self._1client
            print("G")
            if _client is None:
                _client = self._2GetClient()
            print("H")
            print("A")
            for i in range(0, self.tries):
                try:
                    print("B")
                    _client._1headers = {}
                    _client._1headers['User-Agent'] = self.userAgent
                    _client._1headers['X-Line-Application'] = self.app
                    _client._1headers['X-Line-Access'] = self.authToken
                    print("D")
                    #_client.ready()
                    _client.tokenLogin()
                    print("C")
                    _client.setTimeout(3000)
                    return _client
                except TalkException as e:
                    print_exc()
                    self.client.Report("[UserClient._1GetClientAuthToken]\n" + str(e))
                    if e.code == 8:
                        break
                except Exception as e:
                    self.client.Report("[UserClient._1GetClientAuthToken]\n" + format_exc())
                    if isinstance(e, TalkException) and e.code == 8:
                        break
            self.authToken = None
            self.certificate = None
            if self.client.db is not None:
                with self.client.GetCursor() as cur:
                    cur.Execute("DELETE FROM TextVars WHERE name='authToken' or name='certificate'")
                    cur.Commit()
    @property
    def provider(self):
        if IsEmpty(self.email):
            return 0
        if emailRegex.match(self.email):
            return IdentityProvider.LINE # LINE
        return IdentityProvider.NAVER_KR # NAVER
            
    @property
    def osVersion(self):
        if self.isMac:
            return "10.9.4-MAVERICKS-x64"
        return "5.1.2600-XP-x64"
    
    def GetUserAgent(self, version=None):
        if not version:
            version = self.version
        if self.isMac:
            return "DESKTOP:MAC:%s(%s)" % (self.osVersion, version)
        return "DESKTOP:WIN:%s(%s)" % (self.osVersion, version)
    
    def GetApp(self, version=None):
        if not version:
            version = self.version
        if self.isMac:
            return "DESKTOPMAC\t%s\tMAC\t%s" % (version, self.osVersion)
        return "DESKTOPWIN\t%s\tWINDOWS\t%s" % (version, self.osVersion)
    
    @property 
    def userAgent(self):
        return self.GetUserAgent()
    
    @property
    def loginUserAgent(self):
        return self.GetUserAgent(self.loginVersion)
    
    @property 
    def app(self):
        return self.GetApp()
    
    @property
    def loginApp(self):
        return self.GetApp(self.loginVersion)
    
    @property
    def verifier(self):
        return self._1verifier
    
    @verifier.setter
    def verifier(self, value):
        self._1headers["X-LINE-ACCESS"] = value
        self._1verifier = value
        
    def _2GetClient(self):
        return LineAPI(self)
        
                
    def _1GetClient(self, _client = None, tryAuth = True):
        with Acquire(self.lock):
            counter = 0
            while True:
                if _client is None:
                    _client = self._2GetClient()
                err = False
                try:
                    if tryAuth:
                        _client = self._1GetClientAuthToken(_client)
                        print("GOT CLIENT AUTHTOKEN")
                    if not tryAuth or _client is None:
                        if _client is None:
                            tryAuth = False
                            _client = self._2GetClient()
                        _client._1headers = {}
                        _client._1headers['User-Agent'] = self.loginUserAgent
                        print("AUTHTOKEN " + str(self.authToken))
                        pin = _client.login(True)
                        print("PINCODE2 " + pin)
                        self.client.ReportAll("PinCode : " + str(pin) + "\nPlease enter in 2 minutes.")
                        _client.resumeLogin()
                        _client.ready()
                        print("GOT CLIENT EMAIL")
                    self.revision = _client._1getLastOpRevision()
                    #TEST
                    self.authTimer = self.reauthDelay
                    self._1client = _client
                    self._1ready = True
                    _client.setTimeout(3000)
                    return _client
                    break
                except TalkException as e:
                    print_exc()
                    self.client.Report("[UserClient._1GetClient:1]\n" + str(e))
                    err = True
                    tryAuth=False
                except Exception:
                    self.client.Report("[UserClient._1GetClient:1]\n" + format_exc())
                    err = True
                    tryAuth = False
                if err:
                    _client = None
                    counter = counter + 1
                    if counter >= self.tries:
                        counter = 0
                        sleep(900)
            counter = 0
            for i in range(0, self.tries):
                try:
                    print("G")
                    _client = self._1UpdateAuthToken(_client)
                    print("C")
                    
                    self._1client = _client
                    return _client
                except TalkException as e:
                    print_exc()
                    self.client.Report("[UserClient._1GetClient:2]\n" + str(e))
                except Exception:
                    self.client.Report("[UserClient._1GetClient:2]\n" + format_exc())
            return self._1GetClient(tryAuth)
            
    def _1UpdateAuthToken(self, _client = None):
        with Acquire(self.lock):
            self._1ready = False
            if _client is None:
                _client = self._1client
            if _client is None:
                return
            _client.setTimeout(120000)
            try:
                print("UPDATEAUTHTOKEN HEADERS " + str(_client._1headers))
                pin = _client.login(False)
                if isinstance(pin, str):
                    self.client.ReportAll("AuthToken may have expired. PinCode : " + str(pin) + "\nPlease enter in 2 minutes.")
                    if not _client.resumeLogin():
                        raise Exception("AuthToken expired")
                _client.ready()
                self.authTimer = self.reauthDelay
                if self.client.db is not None:
                    with self.client.GetCursor() as cur:
                        print("Z")
                        cur.SetTextVar("authToken", self.authToken, commit=False)
                        cur.SetTextVar("certificate", self.certificate, commit=False)
                        print("AA")
                        cur.Commit()
                        print("AB")
                print("U")
            except Exception:
                print("V")
                self.client.Report("[UserClient._1UpdateAuthToken]\n" + format_exc())
                print("GETCLIENT UPDATEAUTH")
                return self._1GetClient(tryAuth=False)
            print("W")
            _client.setTimeout(3000)
            print("X")
            self._1ready = True
            return _client
            
    def _1Report(self, msg):
        if len(self.adminObjs) > 0:
            return self.adminObjs[0].SendText(msg)
        elif len(self.adminMids) > 0:
            return self._2SendText(self.adminMids[0], msg) 
        raise Exception("[OAClient._1Report : No report Mid]\n" + msg)
        
    def _1ReportAll(self, msg):
        if len(self.adminObjs) > 0:
            return self._1SendText(self.adminObjs, msg)
        elif len(self.adminMids) > 0:
            return self._2SendText(self.adminMids, msg) 
        raise Exception("[OAClient._1Report : No report Mid]\n" + msg)
    
    
    def _1AcceptAllGroupInvitations(self):
        try:
            for gmid in self._1client._1getGroupIdsInvited():
                self._1client._1acceptGroupInvitation(gmid)
        except Exception:
            pass

    def Ping(self):
        while self._1running:
            sleep(self.pingInterval)
            if self.shouldPing:
                p =  RequestsGet(self.pingAddress)
                self.shouldPing = False
            else:
                self.timeUnpinged += self.pingInterval
            
    def Start(self, thread = 0, mode = None):
        if mode is not None:
            self.mode = mode
        if self._1running:
            return
        if mode < 8:
            if thread:
                self.thread = self.client.Thread(self._1Main, [])
                return self.thread
            return self._1Main()
        else:
            if thread == 0:
                self.thread = self.client.Thread(self._2Main, [])
                self.thread2 = self.thread
                return self._1Main()
            elif thread == 1:
                self.thread = self.client.Thread(self._1Main, [])
                return self._2Main()
            else:
                self.thread = self.client.Thread(self._1Main, [])
                self.thread2 = self.client.Thread(self._1Main2, [])
                if thread == 2:
                    return self.thread
                elif thread == 3:
                    return self.thread2
                return [self.thread, self.thread2]
            
    def Stop(self):
        self._1running = False
        self._1ready = False
        self.thread = None
        
                    
        
    def _1GetObjByLineMid(self, mid, msgId = None, obj = None, time =None, hasUser = defaultParameter, init=True, messageText='', userInChatroom=None):
        if mid is None:
            return
        default = False
        if hasUser == defaultParameter:
            hasUser = True
            default = True
        with Acquire(self.lock):
            if mid not in self.midLocks:
                self.midLocks[mid] = Lock()
            lock = self.midLocks[mid]
        with Acquire(lock):
            ret = None
            with Acquire(self.client.lock):
                if mid in self.client._1objectsByLineMid:
                    ret = self.client._1objectsByLineMid[mid]
            if ret:
                if obj is not None:
                    self.client.Thread(ret._1SetObjAndTime, [obj, time])
                if hasUser is not None:
                    ret.hasUser = hasUser
                ret.TrySync()
                if msgId is None or ret.hasOA or (ret.chatroomType == ChatroomType.user and (not userInChatroom or not msgId or not ( msgId in self.client._1senderObjectsUserByMsgId or userInChatroom.hasOA) )) or not self.client.hasOA:
                    return ret
                if messageText.startswith("[INITROOM]"):
                    key = messageText.rpartition(' ')[2]
                    room = self.client._1waitingRoom.pop(key, None)
                    if room:
                        ret.Sync(room)
                msgFound = False
                if msgId:
                    with Acquire(self.client.lock):
                        obj2 = None
                        if ret.chatroomType == ChatroomType.user:
                            if msgId in self.client._1senderObjectsOAByMsgId:
                                obj2 = self.client._1senderObjectsOAByMsgId[msgId]
                        else:
                            if msgId in self.client._1objectsOAByMsgId:
                                obj2 = self.client._1objectsOAByMsgId[msgId]
                        if obj2:
                            print("Merging chatroom")
                            ret.Sync(obj2)
                            msgFound = True
                if not msgFound:
                    if self.client.db is not None:
                        with self.client.GetCursor() as cur:
                            cur.Execute("SELECT lineId, hasOA, hasUser, id, uId FROM ChatRooms WHERE lineMid=%s", (mid,))
                            f = cur.FetchOne()
                            if f is not None and f[0]:
                                ret.id = f[0]
                                ret.hasOA = f[1]
                                if f[2] != hasUser:
                                    if default:
                                        ret.hasUser = f[2]
                                    else:
                                        cur.Execute("UPDATE ChatRooms SET hasUser=%s WHERE id=%s", (ret._2hasUser, f[3]))
                                        cur.Commit()
                                ret._2id = f[3]
                                if ret.chatroomType == ChatroomType.room:
                                    ret.uId = f[4]
                                with Acquire(self.client.lock):
                                    if ret.id in self.client._1objectsByLineId:
                                        ret.Sync(self.client._1objectsByLineId[ret.id])
                    if self.client.hasOA:
                        with Acquire(self.client.lock):
                            if ret.chatroomType == ChatroomType.user:
                                if userInChatroom and (msgId in self.client._1objectsUserByMsgId or userInChatroom.hasOA):
                                    self.client._1senderObjectsUserByMsgId[msgId] = ret
                            else:
                                self.client._1objectsUserByMsgId[msgId] = ret
            else:
                #print("Creating new User for mid " + str(mid))
                isUser = mid[0] == 'u'
                if init:
                    init = obj is None
                if isUser:
                    ret = User(mid = mid, client=self.client, init=init)
                    self.client.users.append(ret)
                    with Acquire(self.client.lock):
                        if msgId and userInChatroom and (msgId in self.client._1objectsUserByMsgId or userInChatroom.hasOA):
                            self.client._1senderObjectsUserByMsgId[msgId] = ret
                        
                else:
                    if mid[0] == 'r':
                        ret = Room(mid = mid, client=self.client, hasUser=hasUser, init=init)
                        self.client.rooms.append(ret)
                    elif mid[0] == 'c':
                        ret = Group(mid = mid, client=self.client, hasUser=hasUser, init=init)
                        self.client.groups.append(ret)
                    else:
                        raise Exception("[UserClient._1GetObjByLineMid : Invalid Id]\n" + id)
                    if msgId is not None:
                        with Acquire(self.client.lock):
                            if self.client.hasOA:
                                self.client._1objectsUserByMsgId[msgId] = ret
                            

                with Acquire(self.client.lock):
                    if mid in self.client._1objectsByLineMid:
                        return self._1GetObjByLineMid(mid)
                    self.client._1objectsByLineMid[mid] = ret
                    if ret.chatroomType == ChatroomType.user:
                        self.client.users.append(ret)
                    if ret.chatroomType == ChatroomType.room:
                        self.client.rooms.append(ret)
                    if ret.chatroomType == ChatroomType.group:
                        self.client.groups.append(ret)
                
                if obj is not None:
                    self.client.Thread(ret._1SetObjAndTime, [obj, time])
                
            if self.client.db is not None:
                #print("self.client.db is not None FOR mid=%s" % mid)
                with self.client.GetCursor() as cur:
                    #print("self.client.GetCursor FOR mid=%s" % mid)
                    if ret.chatroomType == ChatroomType.user:
                        cur.Execute("INSERT INTO Users(lineId, lineMid) Values(%s, %s) ON CONFLICT(lineMid) DO UPDATE SET dummy=True RETURNING id, rId", (ret.id, ret.mid,))
                        f = cur.FetchOne()
                        cur.Commit()
                        ret._2id = f[0]
                        ret.rId = f[1]
                        with Acquire(self.client.lock):
                            self.client._1objectsByUId[ret._2id] = ret
                    else:
                        #print("ret.chatroomType != ChatroomType.user FOR mid=%s" % mid)
                        cur.Execute("SELECT lineId, hasUser, hasOA, id, uId FROM ChatRooms WHERE lineMid=%s", (mid,))
                        fLI = cur.FetchOne()
                        if fLI is None: 
                            #print("fLI is None FOR mid=%s" % mid)
                            b = False
                            if msgId is not None:
                                b = ret.id = self._1CheckMsgId(ret, msgId)
                            if not b:
                                cur.Execute("INSERT INTO ChatRooms(lineMid, type, hasUser) Values(%s, %s, %s) RETURNING id", (ret.mid, ret.chatroomType, ret._2hasUser))
                                f = cur.FetchOne()
                                ret._2id = f[0]
                                cur.Commit()
                        else:
                            #print("fLI is not None FOR mid=%s" % mid)
                            ret._2id = fLI[3]
                            ret.hasOA = fLI[2]
                            if fLI[1] != hasUser:
                                if default:
                                    self.hasUser = fLI[1]
                                else:
                                    cur.Execute("UPDATE ChatRooms SET hasUser=%s WHERE id=%s", (ret._2hasUser, fLM[3],))
                                    cur.Commit()
                            if IsEmpty(fLI[0]):
                                #print("IsEmpty(fLI[0]) FOR mid=%s" % mid)
                                if ret.chatroomType != ChatroomType.user:
                                    ret.id = self._1CheckMsgId(ret, msgId)
                            else:
                                ret.id = fLI[0]
                                #print("not IsEmpty(fLI[0]) FOR mid=%s" % mid)
                            with Acquire(self.client.lock):
                                self.client._1objectsByRId[ret._2id] = ret
                            if ret.chatroomType == ChatroomType.room:
                                ret.uId = fLI[4]
                            if not IsEmpty(ret.id):
                                with Acquire(self.client.lock):
                                    if ret.id in self.client._1objectsByLineId:
                                        ret.Sync(self.client._1objectsByLineId[ret.id])
                    cur.Close()
            ret.TrySync()
            return ret
            
    def _1CheckMsgId(self, obj, msgId):
        with self.client.GetCursor() as cur:
            if obj.chatroomType == ChatroomType.user:
                s = "Sender"
            else:
                s = ""
            cur.Execute("SELECT lineId FROM " + s + "LineIdByMsgId WHERE msgId=%s", (msgId,))
            fLI = cur.FetchOne()
            ret = None
            if fLI is None:
                cur.Execute("INSERT INTO " + s + "LineMidByMsgId(msgId, lineMid) Values(%s, %s) ON CONFLICT(msgId) DO UPDATE SET lineMid=%s", (msgId, obj.mid, obj.mid))
                cur.Commit()
            else:
                obj.id = fLI[0]
                obj.hasOA = True
                if obj.id in self.client._1objectsByLineId:
                    obj.Sync(self.client._1objectsByLineId[obj.id])
                else:
                    obj.Sync()
            return obj.id
        
        
        #TODO
        
    def _1SendText(self, to, text):
        if isinstance(to, list):
            ret = True
            for t in to:
                ret = ret and self._1SendText(t, text)
            return ret
        return self._2SendText(to.mid, text)
    
    
    def _2SendText(self, to, text):
        text = str(text).encode('utf-8')
        message = _Message(toMid=to, text=text)
        try:
            self._1client._1sendMessage(message)
            return True
        except Exception:
            self.client.Report("[UserClient._2SendText]\n" + format_exc())
        return False
    
    def Download(self, url):
        r = RequestsGet(url, headers=self._1headers)
        if r.status_code != 200:
            raise Exception('Download image failure.\nHTTP Code : ' + str(r.status_code) + "\nLink : " + url)
        b = bytes()
        for chunk in r:
            b = b + bytes(chunk)
        return b
    
    def _1SendImageWithBytes(self, to, bytes):
        return self._1SendContentWithBytes(to, bytes, ContentType.IMAGE)
    
    def _1SendAudioWithBytes(self, to, bytes):
        return self._1SendContentWithBytes(to, bytes, ContentType.AUDIO)
    
    def _1SendVideoWithBytes(self, to, bytes):
        return self._1SendContentWithBytes(to, bytes, ContentType.VIDEO)
    
    def _1SendFileWithBytes(self, to, bytes):
        return self._1SendContentWithBytes(to, bytes, ContentType.FILE)
    
    def _1SendImageWithUrl(self, to, url):
        return self._1SendContentWithUrl(to, url, ContentType.IMAGE)
    
    def _1SendAudioWithUrl(self, to, url):
        return self._1SendContentWithUrl(to, url, ContentType.AUDIO)
    
    def _1SendVideoWithUrl(self, to, url):
        return self._1SendContentWithUrl(to, url, ContentType.VIDEO)
    
    def _1SendFileWithUrl(self, to, url):
        return self._1SendContentWithUrl(to, url, ContentType.FILE)
        
    
    def _1SendContentWithUrl(self, to, url, contentType=ContentType.FILE):
        if isinstance(url, list):
            ret = True
            for u in url:
                ret = ret and self._1SendContentWithUrl(to, u, contentType)
            return ret
        return self._1SendContentWithBytes(to, self.Download(url), contentType)
    
    def _1SendContentWithPath(self, to, path, contentType=ContentType.FILE):
        if isinstance(path, list):
            ret = True
            for p in path:
                ret = ret and self._1SendContentWithPath(to, p, contentType)
            return ret
        bytes = None
        with open(path, 'rb') as f:
            bytes = f.read()
        return self._1SendContentWithBytes(to, bytes, contentType)
    
    
    def _1SendContentWithBytes(self, to, bytes, contentType=ContentType.FILE):
        if isinstance(bytes, list):
            ret = True
            for b in bytes:
                ret = ret and self._1SendContentWithBytes(to, b, contentType)
            return ret
        if isinstance(to, list):
            ret = True
            for t in to:
                ret = ret and self._1SendContentWithBytes(t, bytes, contentType)
            return ret
        return self._2SendContentWithBytes(to.mid, bytes, contentType)
        
    
    def _2SendContentWithPath(self, to, path, contentType=ContentType.FILE):
        bytes = None
        with open(path, 'rb') as f:
            bytes = f.read()
        return self._2SendContentWithBytes(to, bytes, contentType)
    
    
    def _2SendContentWithUrl(self, to, url, contentType=ContentType.FILE):
        return self._2SendContentWithBytes(to, self.Download(url), contentType)
        
    def _2SendContentWithBytes(self, to, bytes, contentType=ContentType.FILE):
        message = _Message(toMid=to, text=None)
        message.contentType = contentType
        message.contentPreview = None
        message.contentMetadata = None

        message_id = self._1client._1sendMessage(message).id
        files = {
            'file': bytes,
        }
        params = {
            'name': 'media',
            'oid': message_id,
            'size': len(bytes),
            'type': ContentType._VALUES_TO_NAMES[contentType].lower(),
            'ver': '1.0',
        }
        data = {
            'params': dumps(params)
        }
        r = self._1client.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
        if r.status_code != 201:
            raise Exception('Upload content failure.')
        #r.content
        return True
    
    def _1SendSticker(self, to, packageId, stickerId):
        if isinstance(to, list):
            ret = True
            for t in to:
                ret = ret and self._1SendSticker(t, packageId, stickerId)
            return ret
        return self._2SendSticker(to.mid, packageId, stickerId)
                                   
    def _2SendSticker(self, to, packageId, stickerId):
        message = _Message(toMid=to, text="Location")
        message.hasContent=True
        message.contentType = ContentType.STICKER
        message.contentMetadata = {'STKPKGID' : packageId, 'STKID' : stickerId}

        return self._1client._1sendMessage(message)
        
    
    def _1SendLocation(self, to, title, address, latitude, longitude, phone=None):
        if isinstance(to, list):
            ret = True
            for t in to:
                ret = ret and self._1SendLocation(t, title, address, latitude, longitude, phone)
            return ret
        return self._2SendLocation(to.mid, title, address, latitude, longitude, phone)
    
    def _2SendLocation(self, to, title, address, latitude, longitude, phone=None):
        message = _Message(toMid=to, text="Location")
        message.hasContent=False
        message.contentType = ContentType.NONE
        message.location = Location(title=title, address=address, latitude=latitude, longitude=longitude, phone=hone)

        return self._1client._1sendMessage(message)
        
    
    def ParseOperation(self, op):
        self.shouldPing = True
        opType = op[0]
        sender = op[1]
        chatroom = op[2]
        message = op[3]
        msg = None
        if opType == OpType.NOTIFIED_INVITE_INTO_GROUP:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            chatroomObj.Refresh()
            cond = op[4].param3 == self.mid
            if cond:
                chatroomObj.hasUser = False
                msg = self._1Invited(chatroom = chatroomObj)
            if not cond or self.autoAcceptInvitation:
                try: 
                    chatroomObj.Join()
                except Exception:
                    print_exc()
        elif opType == OpType.NOTIFIED_ADD_CONTACT:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            chatroomObj.Refresh()
            msg = self._1Followed(chatroom = chatroomObj)
        elif opType == OpType.NOTIFIED_UPDATE_PROFILE or opType == OpType.NOTIFIED_UPDATE_GROUP:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            chatroomObj.Refresh()
            msg = self._1Update(chatroom = chatroomObj)
        elif opType == OpType.NOTIFIED_INVITE_INTO_ROOM:
            invitee = op[4].param3
            chatroomObj = self._1GetObjByLineMid(chatroom)
            chatroomObj.Refresh()
            if invitee == self.mid:
                chatroomObj.hasUser = True
                msg = self._1Joined(chatroom = chatroomObj)
            elif invitee == self.client.oAClient.mid:
                chatroomObj.hasOA = True
        elif opType == OpType.ACCEPT_GROUP_INVITATION or opType == OpType.CREATE_GROUP or opType == OpType.CREATE_ROOM:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            chatroomObj.Refresh()
            chatroomObj.hasUser = True
            if self.client.oAClient.obj is not None:
                chatroomObj.Invite(self.client.oAClient.obj)
            msg = self._1Joined(chatroom=chatroomObj)
        elif opType == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            if op[4].param2 == self.client.oAClient.mid:
                chatroomObj.hasOA = True
            chatroomObj.Refresh()
        elif opType == OpType.NOTIFIED_LEAVE_GROUP or opType == OpType.NOTIFIED_LEAVE_ROOM:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            chatroomObj.Refresh()
            left = op[4].param3
            if left == self.mid:
                chatroomObj.hasUser = False
                msg = self._1Left(chatroom = chatroomObj)
            elif left == self.oAClient.mid:
                chatroomObj.hasOA = False
                if self.whenOALeave == WhenOALeave.reinvite:
                    chatroomObj.Invite(self.client.oAClient.obj)
                elif self.whenOALeave == WhenOALeave.leaveToo:
                    chatroomObj.Leave()
        elif opType == OpType.LEAVE_GROUP or opType == OpType.LEAVE_ROOM:
            chatroomObj = self._1GetObjByLineMid(chatroom)
            msg = self._1Left(chatroom = chatroomObj)
        elif opType == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
            if op[4].param3 == self.client.oAClient.mid:
                if self.client.oAClient.obj is None:
                    self.client.oAClient.obj = self._1GetObjByLineMid(self.client.oAClient.mid)
                chatroomObj = self._1GetObjByLineMid(chatroom)
                chatroomObj.Refresh()
                chatroomObj.hasOA = False
                chatroomObj.Invite(self.client.oAClient.obj)
            else:
                if self.client.oAClient.obj is None:
                    self.client.oAClient.obj = self._1GetObjByLineMid(self.client.oAClient.mid)
                chatroomObj = self._1GetObjByLineMid(chatroom)
                kickedObj = self._1GetObjByLineMid(op[4].param3)
                if self.mid is None:
                    text = "[Init4] Please kick me out and reinvite me later."
                elif kickedObj.name is not None:
                    text = "Good bye, " + kickedObj.name
                else:
                    text = "Good bye"
                try:
                    text = str(text).encode('utf-8')
                    message = _Message(toMid=chatroom, text=text)
                    self._1client._1sendMessage(message, exceptionLevel=3)
                    chatroomObj.Refresh()
                except TalkException as e:
                    if e.code == 10:
                        chatroomObj.hasUser = False
                        if self.mid is None:
                            self.mid = kickedObj.mid
                            self.obj = kickedObj.Sync(self.obj)
                            self.client.inited = 5
                            try:
                                self.obj.GetProfile()
                            except Exception as e:
                                pass
                            self.obj.Sync()
                            if self.client.db is not None:
                                with self.client.GetCursor() as cur:
                                    cur.SetTextVar("userMid", self.mid)
                            kicker = self._1GetObjByLineMid(op[4].param2)
                            kicker.SendText("[Init5] If you kicked me out because of my request on [Init4] message, please reinvite me into the group from which you just kicked me out.")
                        msg = self._1Left(chatroom = chatroomObj)
                        
        elif not IsEmpty(sender) and not IsEmpty(chatroom) and message is not None:
            contentType = message.contentType
            msgId = message.id
            emptyMsg = message is None or IsEmpty(message.text)
            if contentType in validContentTypes or not emptyMsg:
                messageText=''
                if contentType == ContentType.NONE and not emptyMsg:
                    messageText = message.text
                chatroomObj = self._1GetObjByLineMid(chatroom, msgId = msgId, messageText=messageText)
                senderObj = None
                if chatroomObj.chatroomType == ChatroomType.user:
                    senderObj = chatroomObj
                else:
                    senderObj = self._1GetObjByLineMid(sender, msgId=msgId, messageText=messageText, userInChatroom=chatroomObj)
                if senderObj != self.client.oAClient.obj:
                    if contentType == ContentType.NONE and not emptyMsg:
                        if message.location:
                            msg = self._1Locationmessage(id=msgId, title=message.location.title, address=message.location.address, latitude=message.location.latitude, longitude=message.location.longitude, chatroom=chatroomObj, sender=senderObj, phone=message.location.phone)
                        else:
                            msg = self._1TextMessage(id=msgId, text=message.text, sender=senderObj, chatroom = chatroomObj)
                    elif contentType in [ContentType.IMAGE, ContentType.AUDIO, ContentType.VIDEO, ContentType.FILE]:
                        url = None
                        public = False
                        try:
                            url = message.contentMetadata.DOWNLOAD_URL
                            public = bool(message.contentMetadata.PUBLIC)
                        except Exception:
                            pass
                        if contentType == ContentType.IMAGE:
                            msg = self._1ImageMessage(id=msgId, sender=senderObj, chatroom = chatroomObj, url=url)
                        if contentType == ContentType.AUDIO:
                            msg = self._1AudioMessage(id=msgId, sender=senderObj, chatroom = chatroomObj, url=url)
                        if contentType == ContentType.VIDEO:
                            msg = self._1VideoMessage(id=msgId, sender=senderObj, chatroom = chatroomObj, url=url)
                        if contentType == ContentType.FILE:
                            msg = self._1FileMessage(id=msgId, sender=senderObj, chatroom = chatroomObj, url=url)
                        #if public:
                        #    msg.hasOA = True
                    elif contentType == ContentType.CONTACT:
                        msg = self._1ContactMessage(id = msgId, sender=senderObj, chatroom = chatroomObj, displayName = message.contentMetadata['displayName'], mid=message.contentMetadata['mid'])
                    elif contentType == ContentType.STICKER:
                        msg = self._1StickerMessage(id = msgId, sender=senderObj, chatroom = chatroomObj, packageId=message.contentMetadata['STKPKGID'], stickerId=message.contentMetadata['STKID'])
                    elif contentType == ContentType.POSTNOTIFICATION:
                        pass
                        
                        
        if msg is not None:
            if self.client.main:
                self.client.AddEvent(msg, True)
            else:
                self.client.Thread(self.client.Handle, [msg, False])
        if opType == OpType.RECEIVE_MESSAGE:
            try:
                self._1client._1sendChatChecked(chatroom, message.id)
                #print("READING CHAT SUCCEEDED")
            except Exception as e:
                self.client.Report("[UserClient.ParseEvent:Reading chat error]\nmsgId='" + str(message.id) + "'\nmessage.text='" + str(message.text) + "\n" + format_exc())
        
            
    def _1Main(self):
        while self._1client is None:
            sleep(5)
        with Acquire(self.lock):
            self._1running = True
            if self.pingAddress and self.pingInterval > 0:
                self.pingThread = self.client.Thread(self.Ping, [])
        while self._1running:
            try:
                then = time()
                ops = self._1client._1fetchOperations(self.revision, 20)
                if ops is None:
                    continue
                opsLen = len(ops)
                if opsLen == 0:
                    continue
                self.revision = max(op.revision for op in ops)
                self._1client.revision = self.revision
                if self.mode < 4:
                    self._1MainChild(ops)
                elif self.mode < 8:
                    t = self.client.Thread(self._1MainChild, [ops])
                    t.join(0.8)
                elif self.mode < 12:
                    with self.opsCond:
                        self.ops.extend(ops)
                        self.opsCond.notifyAll()
                diff = time() - then
                #print("diff %g" % diff)
                if diff < 0.8 and opsLen < 20:
                    sleep(0.8-diff)
                #TEST
                #    self.authTimer = self.authTimer - 0.8
                #else:
                #    self.authTimer = self.authTimer - diff
                #if self.authTimer <= 0:
                #    self._1UpdateAuthToken()
            except TalkException as e:
                print_exc()
                self.client.Report("[UserClient._1Main]\n" + str(e))
                if not self._1running:
                    return
                elif e.code in needAuthErrors:
                    self._1UpdateAuthToken()
                
            except Exception:
                self.client.Report("[UserClient._1Main]\n" + format_exc())
                if not self._1running:
                    return
                
                
                
    def _1Main2(self):
        while True:
            op = None
            if self.opsLen == 0:
                with self.opsCond:
                    while self.opsLen == 0:
                        self.opsCond.wait(1)
            op = self.ops.pop(0)
            if self.mode % 4 < 2:
                self._2MainChild(op)
            else:
                self.client.Thread(self._2MainChild, [op])
                
            
    
    def _1MainChild(self, ops):  
        if ops is None:
            return
        if len(ops) == 0 or len([x for x in ops if x]) == 0:
            return
        self.shouldPing = True
        if self.mode % 4 < 2:
            for op in ops:
                self._2MainChild(op)
        else:
            for op in ops:
                self.client.Thread(self._2MainChild, [op])
            
    def _2MainChild(self, op):
            if op is None:
                return
            if op.type == OpType.END_OF_OPERATION:
                return
            if op.type not in [OpType.RECEIVE_MESSAGE,
                                    OpType.NOTIFIED_UPDATE_PROFILE,
                                    OpType.NOTIFIED_ADD_CONTACT,
                                    OpType.CREATE_GROUP,
                                    OpType.NOTIFIED_INVITE_INTO_GROUP,
                                    OpType.NOTIFIED_ACCEPT_GROUP_INVITATION,
                                    OpType.ACCEPT_GROUP_INVITATION,
                                    OpType.NOTIFIED_UPDATE_GROUP,
                                    OpType.NOTIFIED_LEAVE_GROUP,
                                    OpType.LEAVE_GROUP,
                                    OpType.NOTIFIED_KICKOUT_FROM_GROUP,
                                    OpType.CREATE_ROOM,
                                    OpType.NOTIFIED_INVITE_INTO_ROOM,
                                    OpType.INVITE_INTO_ROOM,
                                    OpType.NOTIFIED_LEAVE_ROOM,
                                    OpType.LEAVE_ROOM]:
                return
            self.shouldPing = True
            raw_message = None
            raw_sender = None
            raw_chatroom = op.param1
            if op.type == OpType.RECEIVE_MESSAGE:
                raw_message  = op.message
                raw_sender   = op.message.fromMid
                raw_receiver = op.message.toMid
                if raw_receiver[0] != 'u':
                    if self.client.hasOA and self.client.oAClient.mid is not None and raw_sender == self.client.oAClient.mid:
                        try:
                            self._1client._1sendChatChecked(raw_chatroom, raw_message.id)
                        except Exception:
                            pass
                        return
                    raw_chatroom = raw_receiver
                else:
                    raw_chatroom = raw_sender
            if not self.client._1started:
                self.client.started=True
            if not IsEmpty(raw_chatroom):
                if self.mode % 2 == 0:
                    self.ParseOperation([op.type, raw_sender, raw_chatroom, raw_message, op])
                else:
                    self.client.Thread(self.ParseOperation, [[op.type, raw_sender, raw_chatroom, raw_message, op]])
        
                    
        
        
        