import ssl



try:
    _create_unverified_https_context = ssl._1create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._1create_default_https_context = _create_unverified_https_context



from traceback import format_exc, print_exc
from tempfile import gettempdir
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage as _TextMessage, TextSendMessage, TemplateSendMessage, TemplateAction, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, ButtonsTemplate, PostbackEvent, CarouselTemplate, CarouselColumn, LeaveEvent, FollowEvent, UnfollowEvent, JoinEvent, ImageSendMessage, ImageMessage as _ImageMessage, VideoMessage as _VideoMessage, AudioMessage as _AudioMessage, LocationMessage as _LocationMessage, VideoSendMessage, AudioSendMessage, LocationSendMessage, StickerMessage as _StickerMessage, StickerSendMessage

from .api.line_0_10_0.ttypes import TalkException, MIDType, OpType, IdentityProvider, Message as _Message, ContentType
from requests.exceptions import (ReadTimeout, Timeout)

from .api.api import LineAPI, needAuthErrors
from .models.types import Receiver, MessageType, ChatroomType, EventType, UserStatus, UserRelation, WhenOALeave
from .models.events import Joined, Invited, Left, Followed, Unfollowed, Message, TextMessage, ImageMessage, Update, Button, Buttons
from .models.chatrooms import User, Room, Group
from .models.database import Database
from .models.command import defaultParameter
from .utils import IsEmpty, emailRegex, Lock, Alphanumeric, Acquire, CreateBody

from requests import get as RequestsGet, post as RequestsPost

from time import time, sleep

from socket import timeout

from threading import Thread, current_thread

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
        
class OAClient(object):
    
    def __init__(self, client):
        self.lock = Lock()
        with Acquire(client.lock, self.lock):
            self.client = client
        with Acquire(self.lock):
            self.thread = None
                
            self._1client = LineBotApi(self.channelAccessToken)
            if self.channelSecret is None:
                self.parser = None
            else:
                self.parser = WebhookParser(self.channelSecret)
            self.idLocks = {}
            self.adminObjs = []
            self.running = False
            
    @property
    def name(self):
        return self.client.oAName
                    
    @property
    def obj(self):
        return self.client.oAObj
    
    @obj.setter
    def obj(self, value):
        self.client.oAObj = value
                    
    @property
    def mid(self):
        return self.client.oAMid
    
    @mid.setter
    def mid(self, value):
        self.client.oAMid = value
                    
    @property
    def db(self):
        return self.client.db
    
    def GetCursor(self):
        return self.client.db.GetCursor()
                    
    @property
    def adminIds(self):
        return self.client.adminIds
    
    @adminIds.setter
    def adminIds(self, value):
        self.client.adminIds = value
                    
    @property
    def tries(self):
        return self.client.tries
    
    @tries.setter
    def tries(self, value):
        self.client.tries = value
                    
    @property
    def channelSecret(self):
        return self.client.channelSecret
    
    @channelSecret.setter
    def channelSecret(self, value):
        self.client.channelSecret = value
                    
    @property
    def channelAccessToken(self):
        return self.client.channelAccessToken
    
    @channelAccessToken.setter
    def channelAccessToken(self, value):
        self.client.channelAccessToken = value
            
    def _1TextMessage(self, id, text, chatroom, sender = None):
        chatroom.hasOA = True
        return self.client._1TextMessage(id, text, chatroom, Receiver.oA, sender=sender)
    
    def _1StickerMessage(self, id, packageId, stickerId, chatroom, sender = None):
        chatroom.hasOA = True
        return self.client._1StickerMessage(id, packageId, stickerId, chatroom, Receiver.oA, sender=sender)
    
    def _1LocationMessage(self, id, title, address, latitude, longitude, chatroom, sender = None):
        chatroom.hasOA = True
        return self.client._1LocationMessage(id, title, address, latitude, longitude, chatroom, Receiver.oA, sender=sender)
    
    def _1ImageMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasOA = True
        return self.client._1ImageMessage(id, chatroom, Receiver.oA, sender=sender, url=url, bytes=bytes)
    
    def _1AudioMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasOA = True
        return self.client._1AudioMessage(id, chatroom, Receiver.oA, sender=sender, url=url, bytes=bytes)
    
    def _1VideoMessage(self, id, chatroom, sender = None, url=None, bytes=None):
        chatroom.hasOA = True
        return self.client._1VideoMessage(id, chatroom, Receiver.oA, sender=sender, url=url, bytes=bytes)
    
    def _1Update(self, chatroom):
        chatroom.hasOA = True
        return self.client._1Update(chatroom, Receiver.oA)
    
    def _1Unfollowed(self, chatroom):
        chatroom.hasOA = False
        return self.client._1Unfollowed(chatroom, Receiver.oA)
    
    def _1Followed(self, chatroom):
        chatroom.hasOA = True
        return self.client._1Followed(chatroom, Receiver.oA)

    def _1Joined(self, chatroom):
        chatroom.hasOA = True
        return self.client._1Joined(chatroom, Receiver.oA)
        
    def _1Left(self, chatroom):
        chatroom.hasOA = False
        return self.client._1Left(chatroom, Receiver.oA)
    
    def _1Invited(self, chatroom):
        chatroom.hasOA = False
        return self.client._1Invited( chatroom, Receiver.oA)

    
    def _1Report(self, msg):
        if len(self.adminObjs) > 0:
            return self.adminObjs[0].SendText(msg)
        elif len(self.adminIds) > 0:
            return self._2SendText(self.adminIds[0], msg) 
        raise Exception("[OAClient._1Report : No report Id]\n" + msg)
        
    def _1ReportAll(self, msg):
        if len(self.adminObjs) > 0:
            return self._1SendText(self.adminObjs, msg)
        elif len(self.adminIds) > 0:
            return self._2SendText(self.adminIds, msg)
        raise Exception("[OAClient._1Report : No report Id]\n" + msg)
        
        
    
    def _1GetContentRaw(self, msgId):
        for i in range(0, self.tries):
            try:
                return self._1client.get_message_content(msgId)
            except (timeout, ReadTimeout, Timeout):
                pass
        
    def _1GetContent(self, msgId):
        content = self._1GetContentRaw(msgId)
        if content is None:
            return None
        ret = bytes()
        for chunk in content.iter_content():
            ret = ret + bytes(chunk)
        return ret
    
    def _1Leave(self, room):
        if not room.hasOA:
            return False
        #if room.uObj:
        #    room.RemoveLink()
        if room.chatroomType == ChatroomType.room:
            return self._2LeaveRoom(room.id)
        if room.chatroomType == ChatroomType.group:
            return self._2LeaveGroup(room.id)
        raise Exception("[OAClient._1Leave] 'room' is a User")
    
    def _2LeaveRoom(self, lineId):
        ex = ''
        for i in range(0, self.tries):
            try:
                return self._1client.leave_room(lineId)
            except (timeout, ReadTimeout, Timeout):
                pass
        
    def _2LeaveGroup(self, lineId):
        ex = ''
        for i in range(0, self.tries):
            try:
                return self._1client.leave_group(lineId)
            except (timeout, ReadTimeout, Timeout):
                pass
                
    def _1GetProfile(self, user):
        profile0 = self._2GetProfile(user.id)
        user._1SetProfileAndTime(profile0)
        return user._1profile
    

    def _2GetProfile(self, lineId):
        ex = ''
        for i in range(0, self.tries):
            try:
                return self._1client.get_profile(lineId)
            except (timeout, ReadTimeout, Timeout):
                pass
        
        
        
    def _1SendButtons(self, to, buttons):
        if isinstance(to, list):
            for t in to:
                return self._1SendButtons(t, buttons)
        if not to.hasOA:
            raise Exception("[OAClient._1SendButtons] No OA Client")
        carsb = buttons.Build()
        for car in carsb[0]:
            colLen = len(car.template.columns)
            if colLen==0 or (colLen == 1 and len(car.template.columns[-1].actions) == 0):
                continue
            if len(car.template.columns[-1].actions) == 0:
                car.template.columns.remove(car.template.columns[-1])
            self._1PushMessage(to.id, car)
        if carsb[1] is not None:
            self._1PushMessage(to.id, carsb[1])
    
    def _1SendText(self, to, text):
        if isinstance(to, list):
            return self._2SendText([t.id for t in to], text)
        return self._2SendText(to.id, text)
        
        
    def _2SendText(self, to, text):
        if type(to) is list:
            return self._1Multicast(to, TextSendMessage(text=text))
        return self._1PushMessage(to, TextSendMessage(text=text))
    
    def _1SendImageWithBytes(self, to, bytes):
        if self.client.pyImgurKey is None:
            raise Exception("[OAClient._1SendImage] Client.pyImgurKey must be set")
        url = self.client.UploadPyImgur(bytes)
        return self._1SendImageWithUrl(to, url)
    
    def _1SendImageWithUrl(self, to, url):
        if type(to) is list:
            return self._2SendImageWithUrl([t.id for t in to], url)
        return self._2SendImageWithUrl(to.id, url)
    
    
    def _1SendSticker(self, to, packageId, stickerId):
        if type(to) is list:
            return self._1Multicast(to, StickerSendMessage(package_id=packageId, sticker_id=stickerId))
        return self._1PushMessage(to, StickerSendMessage(package_id=packageId, sticker_id=stickerId))
    
    def _1SendLocation(self, to, title, address, latitude, longitude, phone=None):
        if type(to) is list:
            return self._1Multicast(to, LocationSendMessage(title=title, address=address, latitude=latitude, longitude=longitude))
        return self._1PushMessage(to, LocationSendMessage(title=title, address=address, latitude=latitude, longitude=longitude))
    
    def _1SendVideoWithUrl(self, to, url, previewUrl="https://thumb7.shutterstock.com/display_pic_with_logo/677413/595756799/stock-vector-no-preview-rubber-stamp-595756799.jpg"):
        if type(to) is list:
            return self._1Multicast(to, VideoSendMessage(original_content_url=url, preview_image_url=previewUrl))
        return self._1PushMessage(to, VideoSendMessage(original_content_url=url, preview_image_url=previewUrl))
    
    def _1SendAudioWithUrl(self, to, url, duration=240000):
        if type(to) is list:
            return self._1Multicast(to, AudioSendMessage(original_content_url=url, duration=duration))
        return self._1PushMessage(to, AudioSendMessage(original_content_url=url, duration=duration))
        
        
    
    def _2SendImageWithUrl(self, to, url):
        if url.startswith("https://"):
            url = url[8:]
        elif url.startswith("http://"):
            url = url[7:]
        linka = ""
        linkb = ""
        if url.startswith('i.imgur.com'):
            if "?" in url:
                url = "https://" + url + "&"
            else:
                url = "https://" + url + "?"
            linka = url + "maxwidth=1024&maxheight=1024"
            linkb = url + "maxwidth=240&maxheight=240"
        elif url.startswith('memegen.link'):
            url = "https://" + url
            linka = url + "&width=1024&height=1024"
            linkb = url + "&width=240&height=240"
        elif not url.startswith('i.scaley.io'):
            url = "http://" + url
            linka = ScaleyUrl(url, max=1024) 
            linkb = ScaleyUrl(url, max=240)
        #self._2SendText(to, "LinkA : " + linka + "\nLinkB : " + linkb)
        if type(to) is list:
            return self._1Multicast(to, ImageSendMessage(original_content_url=linka, preview_image_url=linkb))
        return self._1PushMessage(to, ImageSendMessage(original_content_url=linka, preview_image_url=linkb))
    
    def _1Multicast(self, ids, msg):
        idslen = len(ids)
        if idslen == 0:
            return False
        if idslen == 1:
            return self._1PushMessage(ids[0], msg)
        
        userIds = []
        roomOrGroupIds = []
        for id in ids:
            t = id[:1]
            if t == 'U':
                userIds.append(id)
            else:
                roomOrGroupIds.append(id)

        ret = True
        if len(userIds) > 0:
            for i in range(0, self.tries):
                try:
                    self._1client.multicast(userIds, msg)
                    break
                except (timeout, ReadTimeout, Timeout):
                    pass
                except LineBotApiError:
                    if i == self.tries-1:
                        self.client.Report("[Multicast:Ids]\n" + str(userIds))
                        self.client.Report("[Multicast:Msg]\n" + str(msg))
                        self.client.Report("[Multicast:Exc]\n" + format_exc())
                        ret = False
                    
        for roomOrGroupId in roomOrGroupIds:
            ret = ret and self._1PushMessage(roomOrGroupId, msg)
        return ret
        
    def _1PushMessage(self, id, msg):
        for i in range(0, self.tries):
            try:
                self._1client.push_message(id, msg)
                return True
            except (timeout, ReadTimeout, Timeout):
                print("[OAClient._1PushMessage:Timeout]\n" + format_exc())
                pass
            except LineBotApiError:
                e = format_exc()
                print("[OAClient._1PushMessage:LineBotApiError:idnmsg]\n" + str(id) + "\n" + str(msg))
                print("[OAClient._1PushMessage:LineBotApiError]\n" + e)
                if i == self.tries-1:
                    if isinstance(msg, TextSendMessage):
                        text = msg.text
                        textLen = len(msg.text)
                        if textLen > 2000:
                            ret = True
                            while textLen > 2000:
                                ret = self._1PushMessage(id, TextSendMessage(text=text[:2000]))
                                text = text[2000:]
                                textLen = len(text)
                            return ret
                        elif msg.text[:12] == "[PushMessage":
                            continue
                    self.client.Report("[PushMessage:Id]\n" + str(id))
                    self.client.Report("[PushMessage:Msg]\n" + str(msg))
                    self.client.Report("[PushMessage:Exc]\n" + e)
                    raise
        return False
        
        
    def _1GetObjByLineId(self, id, msgId = None, hasOA=defaultParameter, init=True, messageText = '', userInChatroom=False):
        if id is None:
            return
        default=False
        if hasOA == defaultParameter:
            hasOA = True
            default=True
        with Acquire(self.lock):
            if id not in self.idLocks:
                self.idLocks[id] = Lock()
            lock = self.idLocks[id]
        with Acquire(lock):
            if id in self.client._1objectsByLineId:
                ret = self.client._1objectsByLineId[id]
                ret.TrySync()
                if msgId is None or ret.hasUser or (ret.chatroomType == ChatroomType.user and (not userInChatroom or not msgId or not (msgId in self.client._1objectsOAByMsgId or userInChatroom.hasUser))) or not self.client.hasUser:
                    return ret
                if messageText.startswith("[INITROOM]"):
                    key = messageText.rpartition(' ')[2]
                    room = self.client._1waitingRoom.pop(key, None)
                    if room:
                        room.Sync(ret)
                msgFound = False
                with Acquire(self.client.lock):
                    obj2 = None
                    if ret.chatroomType == ChatroomType.user:
                        if userInChatroom and msgId in self.client._1senderObjectsUserByMsgId:
                            obj2 = self.client._1senderObjectsUserByMsgId[msgId]
                    else:
                        if msgId in self.client._1objectsUserByMsgId:
                            obj2 = self.client._1objectsUserByMsgId[msgId]
                    if obj2:
                        print("Merging chatroom")
                        obj2.Sync(ret)
                        msgFound = True
                if not msgFound:
                    if self.client.db is not None:
                        with self.client.GetCursor() as cur:
                            cur.Execute("SELECT lineMid, hasUser, hasOA, id, uId FROM ChatRooms WHERE lineId=%s", (id,))
                            f = cur.FetchOne()
                            if f is not None:
                                if f[2] != hasOA:
                                    if default:
                                        ret.hasOA = f[2]
                                    else:
                                        cur.Execute("UPDATE ChatRooms SET hasOA=%s WHERE id=%s", (ret._2hasOA, f[3],))
                                        cur.Commit()
                                ret._2id = f[3]
                                if ret.chatroomType == ChatroomType.room:
                                    ret.uId = f[4]
                                ret.mid = f[0]
                                ret.hasUser = f[1]
                                if ret.mid:
                                    synced = False
                                    with Acquire(self.client.lock):
                                        if ret.mid in self.client._1objectsByLineMid:
                                            self.client._1objectsByLineMid[ret.mid].Sync(ret)
                                            synced = True
                    with Acquire(self.client.lock):
                        if ret.chatroomType == ChatroomType.user:
                            if userInChatroom and (msgId in self.client._1objectsOAByMsgId or userInChatroom.hasUser):
                                self.client._1senderObjectsOAByMsgId[msgId] = ret
                        else:
                            self.client._1objectsOAByMsgId[msgId] = ret
            else:
                #print("Creating new User for id " + str(id))
                isUser = id[0] == 'U'
                if isUser:
                    ret = User(id=id, client=self.client, init=init)
                    if msgId and userInChatroom and (msgId in self.client._1objectsOAByMsgId or userInChatroom.hasUser):
                        self.client._1senderObjectsOAByMsgId[msgId] = ret
                else:
                    if id[0] == 'R':
                        ret = Room(id=id, client=self.client, hasOA=hasOA, init=init)
                    elif id[0] == 'C':
                        ret = Group(id=id, client=self.client, hasOA=hasOA, init=init)
                    else:
                        raise Exception("[OAClient.GetObjByLineId : Invalid Id]\n" + id)
                    if msgId and self.client.hasUser:
                        self.client._1objectsOAByMsgId[msgId] = ret

                with Acquire(self.client.lock):
                    if id in self.client._1objectsByLineId:
                        return self._1GetObjByLineId(id)
                    self.client._1objectsByLineId[id] = ret
                    if ret.chatroomType == ChatroomType.user:
                        self.client.users.append(ret)
                    if ret.chatroomType == ChatroomType.room:
                        self.client.rooms.append(ret)
                    if ret.chatroomType == ChatroomType.group:
                        self.client.groups.append(ret)
                    

            if self.client.db is not None:
                with self.client.GetCursor() as cur:

                    cur.Execute("SELECT lineMid, hasOA, hasUser, id, uId FROM ChatRooms WHERE lineId=%s", (id,))
                    fLM = cur.FetchOne()
                    if fLM is None: 
                        b = False
                        if ret.chatroomType != ChatroomType.user and msgId is not None:
                            b = self._1CheckMsgId(ret, msgId)
                        if not b:
                            cur.Execute("INSERT INTO ChatRooms(lineId, type, hasOA) Values(%s, %s, %s) RETURNING id", (ret.id, ret.chatroomType, ret._2hasOA))
                            f = cur.FetchOne()
                            ret._2id = f[0]
                            cur.Commit()
                    else:
                        ret._2id = fLM[3]
                        ret.hasUser = fLM[2]
                        if fLM[1] != hasOA:
                            if default:
                                ret.hasOA = fLM[1]
                            else:
                                cur.Execute("UPDATE ChatRooms SET hasOA=%s WHERE id=%s", (ret._2hasOA, fLM[3],))
                                cur.Commit()
                        if IsEmpty(fLM[0]):
                            if ret.chatroomType != ChatroomType.user:
                                ret.mid = self._1CheckMsgId(ret, msgId)
                        else:
                            ret.mid = fLM[0]
                        if ret.chatroomType == ChatroomType.room:
                            ret.uId = fLM[4]
                        if self.client.hasUser and not IsEmpty(ret.mid):
                            with Acquire(self.client.lock):
                                if ret.mid in self.client._1objectsByLineMid:
                                    self.client._1objectsByLineMid[ret.mid].Sync(ret)
            ret.TrySync()
            return ret
    
    def _1CheckMsgId(self, obj, msgId):
        with self.client.GetCursor() as cur:
            if obj.chatroomType == ChatroomType.user:
                s = "Sender"
            else:
                s = ""
            cur.Execute("SELECT lineMid FROM " + s + "LineMidByMsgId WHERE msgId=%s", (msgId,))
            fLM = cur.FetchOne()
            ret = None
            if fLM is None:
                cur.Execute("INSERT INTO " + s + "LineIdByMsgId(msgId, lineId) Values(%s, %s) ON CONFLICT(msgId) DO UPDATE SET lineId=%s", (msgId, obj.id, obj.id,))
                cur.Commit()
            else:
                obj.mid = fLM[0]
                obj.hasUser = True
                if obj.mid in self.client._1objectsByLineMid:
                    self.client._1objectsByLineMid[obj.mid].Sync(obj)
                else:
                    obj.Sync()
            return obj.mid
        
    
    def HandleWebhook(self, environ, start_response):
        # check request method
        if environ['REQUEST_METHOD'] != 'POST':
            start_response('405 Method Not Allowed : ' + environ['REQUEST_METHOD'], [])
            return CreateBody('Method not allowed')

        # get X-Line-Signature header value
        signature = environ['HTTP_X_LINE_SIGNATURE']

        # get request body as text
        wsgi_input = environ['wsgi.input']
        content_length = int(environ['CONTENT_LENGTH'])
        body = wsgi_input.read(content_length).decode('utf-8')

        # parse webhook body
        try:
            events = self.parser.parse(body, signature)
        except InvalidSignatureError:
            start_response('400 Bad Request', [])
            return CreateBody('Bad request')

        # if event is MessageEvent and message is TextMessage, then echo text
        exc = ''
        msg = None
        for event in events:
            self.client.Thread(self.ParseEvent, [event])

        start_response('200 OK', [])
        return CreateBody('OK')

    
    def Start(self, thread=True, port=None):
        
        if self.thread is not None and self.thread.isAlive:
            return self.thread
        if port is None:
            port0 = os.environ.get("PORT", None)
            if port0 is None:
                return
            port = int(port0)
        self.running = True
        if thread:
            self.thread = self.client.Thread(self._1Main, [port])
            return self.thread
        self._1Main(port)
        self.running = False
    
    def _1Main(self, port=None):
        if port is None:
            port0 = os.environ.get("PORT", None)
            if port0 is None:
                return
            port = int(port0)

        self.running = True
        srv = make_server('0.0.0.0', port, self.HandleWebhook)
        srv.serve_forever()
        self.running = False
    
    def ParseEvent(self, event):
        while not self.client.started:
            with self.client.startCond:
                self.client.startCond.wait(1)
        try:
            msg = None
            if isinstance(event, MessageEvent):
                if event.message:
                    messageText = ''
                    if isinstance(event.message, _TextMessage):
                        messageText = event.message.text
                    chatroomObj = self._1GetObjByLineId(id=event.source.sender_id, msgId = event.message.id, messageText=messageText)
                    sender=None
                    if chatroomObj.chatroomType == ChatroomType.user:
                        sender = chatroomObj
                    if not sender and chatroomObj.chatroomType != ChatroomType.user:
                        try:
                            senderId = event.source.user_id
                        except Exception:
                            pass
                        if senderId:
                            sender = self._1GetObjByLineId(id=senderId, msgId = event.message.id, messageText=messageText, userInChatroom = chatroomObj)
                    if isinstance(event.message, _TextMessage):
                        msg = self._1TextMessage(id=event.message.id, text=event.message.text, chatroom = chatroomObj, sender=sender)
                    if isinstance(event.message, _StickerMessage):
                        msg = self._1StickerMessage(id=event.message.id, packageId=event.message.package_id, stickerId = event.message.sticker_id, chatroom = chatroomObj, sender=sender)
                    if isinstance(event.message, _LocationMessage):
                        msg = self._1LocationMessage(id=event.message.id, title=event.message.title, address=event.message.address, latitude=event.message.latitude, longitude=event.message.longitude, chatroom = chatroomObj, sender=sender)
                    if isinstance(event.message, _ImageMessage):
                        msg = self._1ImageMessage(id=event.message.id, chatroom = chatroomObj, sender=sender)
                    if isinstance(event.message, _AudioMessage):
                        msg = self._1AudioMessage(id=event.message.id, chatroom = chatroomObj, sender=sender)
                    if isinstance(event.message, _VideoMessage):
                        msg = self._1VideoMessage(id=event.message.id, chatroom = chatroomObj, sender=sender)
                else:
                    print("UNKNOWN MESSAGE " + str(event))
            else:
                chatroomObj = self._1GetObjByLineId(id=event.source.sender_id)
                if isinstance(event, LeaveEvent):
                    chatroomObj.hasOA = False
                    msg = self._1Left(chatroom = chatroomObj)
                elif isinstance(event, FollowEvent):
                    chatroomObj.hasOA = True
                    msg = self._1Followed(chatroom = chatroomObj)
                elif isinstance(event, UnfollowEvent):
                    chatroomObj.hasOA = False
                    msg = self._1Unfollowed(chatroom = chatroomObj)
                elif isinstance(event, JoinEvent):
                    chatroomObj.hasOA = True
                    msg = self._1Joined(chatroom = chatroomObj)
            if msg is not None and (msg.eventType != EventType.message or not (msg.chatroom.hasUser and self.client.userClient.running)):
                if self.client.main:
                    self.client.AddEvent(msg)
                else:
                    self.client.Thread(self.client.Handle, [msg, False])
        except Exception as ex:
            err = format_exc()
            print(err)
            self.client.Report("[OAClient.ParseEvent]\n" + err)
    
    
        
        