from line2.models.types import Type, EventType, ChatroomType, MessageType, Receiver, ContentType
from line2.models.messages import Buttons, Button, OAOnlyMessage
from line2.utils import IsEmpty
from line2.models.content import Download, ScaleyUrl, UploadPyImgur, Image, Content
    
class Event(object):
    def __init__(self, client, chatroom, receiver):
        if chatroom is None:
            raise Exception("[Event : chatroom is None]")
        self.chatroom = chatroom
        self.client = client
        self.type = Type.event
        self.eventType = None
        self.receiver = receiver
        
        hasUser = False
        hasOA = False
        if chatroom.chatroomType == ChatroomType.user:
            if receiver == Receiver.oA:
                hasOA = True
            elif receiver == Receiver.user:
                hasUser = True
        else:
            hasUser = chatroom.hasUser
            hasOA = chatroom.hasOA
        self.hasUser = hasUser
        self.hasOA = hasOA
        
    #@property
    #def hasUser(self):
    #    return chatroom.hasUser
    
    #@property
    #def haOA(self):
    #    return chatroom.hasOA
        
class Update(Event):
    def __init__(self, client, chatroom, receiver):
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.update
        
class Unfollowed(Event):
    def __init__(self, client, chatroom, receiver):
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.unfollowed
        
class Followed(Event):
    def __init__(self, client, chatroom, receiver):
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.followed

class Joined(Event):
    def __init__(self, client, chatroom, receiver):
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.joined
        
class Left(Event):
    def __init__(self, client, chatroom, receiver):
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.left
    
class Invited(Event):
    def __init__(self, client, chatroom, receiver = None):
        if receiver is None:
            receiver = Receiver.user
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.invited
        
    def Accept(self):
        return self.chatroom.Join()
        
    def Join(self):
        return self.chatroom.Join()
        
        
class Message(Event):
    
    def __init__(self, client, id, chatroom, receiver, sender = None):
        Event.__init__(self, client, chatroom, receiver)
        self.eventType = EventType.message
        self.id = id
        self.messageType = None
        self.sender = None
        self.text = None
        self.image = None
        self.packageId = None
        self.stickerId = None
        self.contentType = None
        self.Set(chatroom, sender)
            
    def Set(self, chatroom, sender = None):
        self.sender = sender
        self.chatroom = chatroom
        if self.sender is None and chatroom.chatroomType == ChatroomType.user:
            self.sender = chatroom
            
    def ReplyText(self, text, event=None):
        if event is None:
            event = self
        return self.chatroom.SendText(text, event)
            
    def ReplyTextOA(self, text, event=None):
        if event is None:
            event = self
        return self.chatroom.SendTextOA(text, event)
            
    def ReplyTextUser(self, text, event=None):
        if event is None:
            event = self
        return self.chatroom.SendTextUser(text, event)
        
    def ReplyImageWithUrl(self, url):
        return self.chatroom.SendImageWithUrl(url)
        
    def ReplyImage(self, url):
        return self.chatroom.SendImage(url)
    
    def ReplyButtons(self, buttons):
        return self.chatroom.SendButtons(buttons)
    
class ContentMessage(Message):
    def __init__(self, client, id, chatroom, receiver, sender = None, url = None, bytes = None):
        Message.__init__(self, client, id, chatroom, receiver, sender)
        self.messageType = MessageType.content
        if url is None and id is not None and self.hasUser:
            url = "http://os.line.naver.jp/os/m/" + str(id)
            
        self.content = Content(client=client, message=self, url=url, bytes=bytes)
        
    def GetContent(self):
        if self.hasOA and self.chatroom.hasOA and self.id is not None:
            self.content._1bytes = self.sender.client.oAClient._1GetContent(self.id)
        return self.content._1bytes
            
    @property
    def url(self):
        return self.content.url
    
    @url.setter
    def url(self, value):
        self.content.url = value
        
    @property
    def bytes(self):
        return self.content.bytes
    
    @bytes.setter
    def bytes(self, value):
        self.content.bytes = value
        
    def Download(self):
        return self.content.Download()
    
    @property
    def stream(self):
        return self.content.stream
    
    @stream.setter
    def stream(self, value):
        self.content.stream = value
    
    def open(self):
        return self.stream
    
    @property
    def file(self):
        return self.stream
    
class ImageMessage(ContentMessage):
    def __init__(self, client, id, chatroom, receiver, sender = None, url = None, bytes = None):
        ContentMessage.__init__(self, client, id, chatroom, receiver, sender, url, bytes)
        self.contentType = ContentType.IMAGE
        self.content = Image(client=client, message=self, url=url, bytes=bytes)
        
    @property
    def image(self):
        return self.content
    
    @image.setter
    def image(self, value):
        self.content = value
    
    def ScaleyURL(url, max=1024):
        return self.image.ScaleyURL(self.url, max)
    
    @property
    def imgurUrl(self):
        return self.image.imgurUrl

    def UploadPyImgur(self):
        return self.image.UploadPyImgur()
    
class TextMessage(Message):
    def __init__(self, client, id, text, chatroom, receiver, sender = None):
        Message.__init__(self, client, id, chatroom, receiver, sender)
        self.messageType = MessageType.text
        self.text = text
    
class ContactMessage(Message):
    def __init__(self, client, id, displayName, mid, chatroom, receiver, sender = None):
        Message.__init__(self, client, id, chatroom, receiver, sender)
        self.messageType = MessageType.contact
        self.displayName = displayName
        self.mid = mid
        
    @property
    def contact(self):
        if client.hasUser:
            return self.client.userClient._1GetObjByLineMid(self.mid)
        return None
        
class StickerMessage(Message):
    def __init__(self, client, id, packageId, stickerId, chatroom, receiver, sender=None):
        Message.__init__(self, client, id, chatroom, receiver, sender)
        self.messageType = MessageType.sticker
        self.packageId = packageId
        self.stickerId = stickerId
        
        
class VideoMessage(ContentMessage):
    def __init__(self, client, id, chatroom, receiver, sender = None, url = None, bytes = None):
        ContentMessage.__init__(self, client, id, chatroom, receiver, sender, url, bytes)
        self.contentType = ContentType.VIDEO
    @property
    def video(self):
        return self.content
    
    @video.setter
    def video(self, value):
        self.content = value

class AudioMessage(ContentMessage):
    def __init__(self, client, id, chatroom, receiver, sender = None, url = None, bytes = None):
        ContentMessage.__init__(self, client, id, chatroom, receiver, sender, url, bytes)
        self.contentType = ContentType.AUDIO
    @property
    def audio(self):
        return self.content
    
    @audio.setter
    def audio(self, value):
        self.content = value

class FileMessage(ContentMessage):
    def __init__(self, client, id, chatroom, receiver, sender = None, url = None, bytes = None):
        ContentMessage.__init__(self, client, id, chatroom, receiver, sender, url, bytes)
        self.contentType = ContentType.FILE
    @property
    def file(self):
        return self.content
    
    @file.setter
    def file(self, value):
        self.content = value

class LocationMessage(Message):
    def __init__(self, client, id, title, address, latitude, longitude, chatroom, receiver, sender=None, phone=None):
        Message.__init__(self, client, id, chatroom, receiver, sender)
        self.messageType = MessageType.location
        self.title=title
        self.address=address
        self.latitude=latitude
        self.longitude=longitude
        self.phone=phone
        
        