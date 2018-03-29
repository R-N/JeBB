from line2.models.types import Type, ChatroomType
from line2.utils import Lock, IsEmpty, Acquire
from threading import Condition
from time import time, sleep
from traceback import format_exc, print_exc, print_stack
from random import randint

rObjQueue = []
rObjCond = Condition()
rObjLock = Lock()

def QueueRObj(user):
    with rObjLock:
        if user not in rObjQueue:
            rObjQueue.append(user)
        with rObjCond:
            rObjCond.notifyAll()
    
def CreateRObj():
    with rObjCond:
        while True:
            while len(rObjQueue) == 0:
                rObjCond.wait()
            with rObjLock:
                user = rObjQueue.pop(0)
                if user.hasUser and user.client.hasOA and user.client.oAClient.obj:
                    l = [user, user.client.oAClient.obj]
                    ret = user.client.CreateRoom(l)
                    #ret = self.client.CreateGroup("RObj #%d" % self._2id, l)
                    #self.SendText("Please accept the group invitation")
                    user.rId = ret._2id
                    ret.uId = user._2id
                    with user.rObjCond:
                        user.rObjCond.notifyAll()
                else:
                    continue
                sleep(2)
                
def StartRObj(client):
    client.Thread(CreateRObj)

class Chatroom(object):
    def __init__(self, id = None, client = None, mid = None):
        self.id = id
        self.client = client
        self.mid = mid
        self._2hasUser = False
        self._2hasOA = False
        self.type = Type.chatroom
        self.lock = Lock()
        self.oLock = Lock()
        self._1time = 0
        self._1name = None
        self._3id = None
        self.key = None
        self._1gettingObj = False
        self.objCond = Condition()
        
    def Sync(self, *args, **kwargs):
        return
        print("SYNCPASS %s" % self)
        
    def TrySync(self, *args, **kwargs):
        return
        print("TRYSYNCPASS %s" % self)
        
    @property
    def gettingObj(self):
        return self._1gettingObj
    
    @gettingObj.setter
    def gettingObj(self, value):
        self._1gettingObj = value
        if not value:
            with self.objCond:
                self.objCond.notifyAll()
                
    def AskGetObj(self):
        with Acquire(self.lock, self.oLock):
            if not self._1gettingObj:
                self._1gettingObj = True
                return True
            return False
                
    def AskMayGetObj(self):
        with Acquire(self.lock, self.oLock):
            if self.mayGetObj:
                self._1gettingObj = True
                return True
            return False
        
    def AskShouldGetObj(self):
        with Acquire(self.lock, self.oLock):
            if self.shouldGetObj:
                self._1gettingObj = True
                return True
            return False
        
    @property
    def mayGetObj(self):
        return not self._1gettingObj and self.hasUser
    
    @mayGetObj.setter
    def mayGetObj(self, value):
        self.gettingObj = value
    
    @property
    def shouldGetObj(self):
        return not self.time and self.mayGetObj
    
    @shouldGetObj.setter
    def shouldGetObj(self, value):
        self.mayGetObj = value
        
    def __hash__(self):
        return hash(str(self.id) + str(self.mid))
        
    def __eq__(self, other):
        return self is other or (isinstance(other, Chatroom) and ((not IsEmpty(self.mid) and self.mid == other.mid) or (not IsEmpty(self.id) and self.id == other.id)))
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    @property
    def _2id(self):
        with Acquire(self.lock):
            return self._3id
    
    @_2id.setter
    def _2id(self, value):
        with Acquire(self.lock):
            self._3id = value
    
        
    @property
    def name(self):
        with Acquire(self.lock):
            return self._1name
    
    @name.setter
    def name(self, value):
        with Acquire(self.lock):
            self._1name = value
        
    @property
    def time(self):
        with Acquire(self.lock):
            return self._1time
    
    @time.setter
    def time(self, value):
        with Acquire(self.lock):
            self._1time = value
        
    @property
    def chatroomType(self):
        t = ''
        if self.id is None:
            t = 'id'
            c = self.mid[0]
        elif self.mid is None:
            t = 'mid'
            c = self.id[0].lower()
        else:
            t = 'mid and id'
            c1 = self.mid[0]
            c2 = self.id[0].lower()
            if c1 != c2:
                raise Exception("[chatroomType] Id and Mid type don't match")
            c = c1
        if c == 'u':
            return ChatroomType.user
        if c == 'r':
            return ChatroomType.room
        if c == 'c':
            return ChatroomType.group
        raise Exception("[chatroomType] Invalid " + t)
        
            
    
    def SendText(self, text, event=None):
        return self.client.SendText(self, text, event)
    
    def SendTextOA(self, text, event=None):
        return self.client.SendTextOA(self, text, event)
    
    def SendTextUser(self, text, event=None):
        return self.client.SendTextUser(self, text, event)
        
    def SendImageWithUrl(self, url):
        return self.client.SendImageWithUrl(self, url)
        
    def SendImage(self, url):
        return self.client.SendImage(self, url)
    
    def SendButtons(self, buttons):
        return self.client.SendButtons(self, buttons)
    
    @property
    def _1hasUser(self):
        #with Acquire(self.lock):
            return self._2hasUser and not IsEmpty(self.mid)
    
    @_1hasUser.setter
    def _1hasUser(self, value):
        if self._2hasUser != value:
            with Acquire(self.lock):
                if self._2hasUser != value:
                    self._2hasUser = value
    
    @property
    def _1hasOA(self):
        #with Acquire(self.lock):
            return self._2hasOA and not IsEmpty(self.id)
    
    @_1hasOA.setter
    def _1hasOA(self, value):
        if self._2hasOA != value:
            with Acquire(self.lock):
                self._2hasOA = value
                
    @property
    def hasUser(self):
        #with Acquire(self.lock):
            return self.client.hasUser and self._1hasUser
    @hasUser.setter
    def hasUser(self, value):
        if self._2hasUser != value:
            with Acquire(self.lock):
                self._1hasUser = value
                self._2hasUser = value
    
    @property
    def hasOA(self):
        #with Acquire(self.lock):
            return self.client.hasOA and self._1hasOA
    @hasOA.setter
    def hasOA(self, value):
        if self._2hasOA != value:
            with Acquire(self.lock):
                self._1hasOA = value
                self._2hasOA = value
                
    @property
    def isAdmin(self):
        return False
        
    
class User(Chatroom):
    def __init__(self, id = None, client = None, mid = None, init = True, rId = None):
        Chatroom.__init__(self, id, client, mid)
        self._1profile = Profile()
        self.rLock = Lock()
        self.rObjCond = Condition()
        self._3id = None
        self._1rId = None
        if rId is not None:
            self._1SetRId(rId)
        self._2hasUser = True
        self._2hasOA = True
        if init:
            self.client.Thread(self.GetProfile)
            
    def Sync(self, obj2 = None):
        if obj2 is None:
            obja = None
            if self.client.hasOA and (not IsEmpty(self.id)) and self.id in self.client._1objectsByLineId:
                obja = self.client._1objectsByLineId[self.id]
            objb = None
            if self.client.hasUser and (not IsEmpty(self.mid)) and self.mid in self.client._1objectsByLineMid:
                objb = self.client._1objectsByLineMid[self.mid]
            if obja is self:
                obj2 = objb
            else:
                obj2 = obja
        if obj2 is self:
            return self
        if obj2 is not None:
            with Acquire(self.lock, obj2.lock, self.oLock, obj2.oLock, self.rLock, obj2.rLock):
                if self.chatroomType != obj2.chatroomType:
                    raise Exception("[Sync] self and obj2 is not of the same type")
                if not IsEmpty(self.id):
                    obj2.id = self.id
                elif not IsEmpty(obj2.id):
                    self.id = obj2.id
                if not IsEmpty(self.mid):
                    obj2.mid = self.mid
                elif not IsEmpty(obj2.mid):
                    self.mid = obj2.mid
                try:
                    with Acquire(self.client.lock):
                        self.client.users.remove(obj2)
                except Exception:
                    pass
                with Acquire(self.rLock, obj2.rLock):
                    r = None
                    if self.rId:
                        r = obj2.rObj
                        obj2.rId = self.rId
                    elif obj2.rId:
                        r = self.rObj
                        self.rId = obj2.rId
                    if r and r.chatroomType != ChatroomType.user:
                        r.uId = self._2id
                if self.rId:
                    with Acquire(self.client.lock):
                        self.client._1objectsByUId[self._2id] = self
                with Acquire(self.oLock, obj2.oLock):
                    if self.time < obj2.time:
                        self.profile = obj2.profile
                    else:
                        obj2.profile = self.profile

        #print("Syncing mid=%s" % self.mid)
        with Acquire(self.client.lock):
            self.client._1objectsUserByMsgId =  { k:v for k, v in self.client._1senderObjectsUserByMsgId.items() if v is not obj2 and v is not self } 
            self.client._1objectsOAByMsgId =  { k:v for k, v in self.client._1senderObjectsOAByMsgId.items() if v is not obj2 and v is not self } 
            self.client._1objectsByLineId[self.id] = self
            self.client._1objectsByLineMid[self.mid] = self
            if self.key and self.key in self.client._1waitingRoom:
                del self.client._1waitingRoom[self.key]
            if obj2.key and obj2.key in self.client._1waitingRoom:
                del self.client._1waitingRoom[obj2.key]
            obj2.key = None
            self.key = None
            #print("Syncing mid=%s to DB" % self.mid)
            if self.client.db is not None and not IsEmpty(self.id) and not IsEmpty(self.mid):
                with self.client.GetCursor() as cur:
                    #print("Syncing mid=%s to DB 2" % self.mid)
                    cur.Execute("SELECT id, lineId, lineMid FROM Users WHERE lineId=%s OR lineMid=%s ORDER BY lineMid DESC", (self.id, self.mid))
                    fs = cur.FetchAll()
                    lenfs = len(fs)
                    id = None
                    if lenfs == 0:
                        #print("Syncing mid=%s to DB lenfs == 0:" % self.mid)
                        cur.Execute("INSERT INTO Users(lineId, lineMid) Values(%s,%s) RETURNING id", (self.id, self.mid,))
                        id = cur.FetchOne()[0]
                        cur.Commit()
                    elif lenfs > 2:
                        #print("Syncing mid=%s to DB lenfs > 2" % self.mid)
                        raise Exception("LENFS > 2 HOW DID THIS EVEN HAPPEN")
                    else:
                        if lenfs == 2:
                            #print("Syncing mid=%s to DB lenfs == 2" % self.mid)
                            cur.Execute("DELETE FROM Users WHERE id=%s", (fs[1][0],))
                            cur.Commit()
                        f = fs[0]
                        id = f[0]
                        if IsEmpty(f[2]):
                            #print("Syncing mid=%s to DB IsEmpty(f[2])" % self.mid)
                            cur.Execute("UPDATE Users SET lineMid=%s WHERE id=%s", (self.mid, id))
                            cur.Commit()
                        elif IsEmpty(f[1]):
                            #print("Syncing mid=%s to DB IsEmpty(f[1])" % self.mid)
                            cur.Execute("UPDATE Users SET lineId=%s WHERE id=%s", (self.id, id))
                            cur.Commit()

                    self._2id = id
                    cur.Execute("DELETE FROM SenderLineIdByMsgId WHERE lineId=%s", (self.id,))
                    cur.Commit()
                    cur.Execute("DELETE FROM SenderLineMidByMsgId WHERE lineMid=%s", (self.mid,))
                    cur.Commit()
            
    @property
    def isAdmin(self):
        return self in self.client.adminObjs
            
    def RemoveLink(self):
        rObj = self.rObj
        if rObj:
            rObj.uId = None
            with self.client.GetCursor() as cur:
                cur.Execute("UPDATE ChatRooms SET uId=NULL WHERE id=%s", (rObj._2id,))
                cur.Commit()
        self.rId = None
        with self.client.GetCursor() as cur:
            cur.Execute("UPDATE Users SET rId=NULL WHERE id=%s", (self._2id,))
            cur.Commit()
            
    @property
    def uId(self):
        if self.hasOA:
            return self._2id
            
    @property
    def uObj(self):
        if self.hasOA:
            return self
        
    
    @property
    def _2id(self):
        with Acquire(self.lock, self.rLock):
            return self._3id
    
    @_2id.setter
    def _2id(self, value):
        with Acquire(self.lock, self.rLock):
            self._3id = value
            r = None
            if self._1rId is not None:
                r = self.rObj
            if r and r!=self:
                r.uId = value
            
    @property
    def hasOA(self):
        #with Acquire(self.lock):
            return self._1hasOA and self.client.hasOA
    
    @hasOA.setter
    def hasOA(self, value):
        if self._2hasOA != value:
            with Acquire(self.lock):
                self._1hasOA = value
                self._2hasOA = value
            
    @property
    def _1hasOA(self):
        #with Acquire(self.lock):
            return not IsEmpty(self.id) and not self.blocked
    
    @_1hasOA.setter
    def _1hasOA(self, value):
        if self._2hasOA != value:
            with Acquire(self.lock):
                self._2hasOA = value
    
    @property
    def rObj(self):
        with self.rObjCond:
            if self.hasOA:
                return self
            ret = None
            if self._1rId:
                ret = self.client.GetObjByRId(self._1rId)
            if not ret or not ret.hasUser:
                return self.CreateRObj()
            ret.InitRoom(True)
            if ret:
                members = ret.members
                if self not in members:
                    if ret.chatroomType == ChatroomType.group:
                        invitees = ret.invitees
                        if self not in invitees:
                            ret.Invite(self)
                        self.SendText("Please accept the group invitation")
                    else:
                        self.SendText("Please invite %s into this room" % self.client.oAName)
                        #self.SendText("Please type '/robj' in a room only consisting of you, %s, and %s" % (self.client.oAName, self.client.userName))
                    return None
                elif self.client.hasOA and self.client.oAClient.obj and (not ret.hasOA or self.client.oAClient.obj not in members):
                    ret.Invite(self.client.oAClient.obj)
            return ret
        
    @rObj.setter
    def rObj(self, value):
        if value is None:
            self.rId = None
            return
        self.rId = value._2id
        
    def CreateRObj(self):
        if self.hasUser and self.client.hasOA and self.client.oAClient.obj:
            l = [self, self.client.oAClient.obj]
            try:
                ret = self.client.CreateRoom(l)
            except TalkException as e:
                if e.code != 35:
                    raise
                try:
                    ret = self.client.CreateGroup("RObj #%d" % self._2id, l)
                    self.SendText("Please accept the group invitation")
                except TalkException as e:
                    if e.code != 35:
                        raise
                    self.SendText("Please type '/robj' in a room only consisting of you, %s, and %s" % (self.client.oAName, self.client.userName))
            self.rId = ret._2id
            ret.uId = self._2id
            
            return self.rObj
            
    @property
    def rId(self):
        with Acquire(self.rLock):
            return self._1rId
    
    @rId.setter
    def rId(self, value):
        with Acquire(self.rLock):
            if value != self._1rId:
                self._1SetRId(value)
            
    def _1SetRId(self, value):
        with Acquire(self.rLock, self.client.lock):
            if value != self._1rId:
                self._1rId = value
                #print("SET RID TO " + str(self._1rId))
                if self.mid:
                    with self.client.GetCursor() as cur:
                        #print("UPDATING USERS")
                        cur.Execute("UPDATE Users SET rId=%s WHERE id=%s OR lineMid=%s", (value, self._2id, self.mid))
                        #print("UPDATED USERS ROWCOUNT " + str(cur.rowCount))
                        cur.Commit()
    
        
    def _1SetObjAndTime(self, obj, t = None):
        with Acquire(self.lock, self._1profile.lock, self.oLock):
            if t is None:
                t = time()
            self._1profile.time = t
            self._1profile.name = obj.displayName
            self._1profile.statusMessage = obj.statusMessage
            self._1profile.capableBuddy = obj.capableBuddy
            self._1profile.relation = obj.relation
            self._1profile.status = obj.status
            self._1profile.type = obj.type
            self._1profile.picUrl = "http://dl.profile.line.naver.jp" + obj.picturePath
            self._1profile.time = t
        self.gettingObj = False
        
    def _1SetProfileAndTime(self, profile, t = None):
        with Acquire(self.lock, self._1profile.lock, self.oLock):
            if t is None:
                t = time()
            self._1profile.time = t
            self._1profile.name = profile.display_name
            self._1profile.statusMessage = profile.status_message
            self._1profile.picUrl = profile.picture_url
        
    def Refresh(self):
        return self.GetProfile().name is not None
    
    @property
    def blocked(self):
        if self.time:
            return self._1profile.blocked
        with Acquire(self.oLock, self._1profile.lock):
            return self._1profile.blocked
    
    @property
    def isOA(self):
        if self.time:
            return self._1profile.isOA
        with Acquire(self.oLock, self._1profile.lock):
            return self._1profile.isOA
        
    @property
    def status(self):
            return self.profile.status
    
    @property
    def capableBuddy(self):
            return self.profile.capableBuddy
    
    @property
    def relation(self):
            return self.profile.relation
    
    @property
    def statusMessage(self):
            return self.profile.statusMessage
    
    @property
    def picUrl(self):
            return self.profile.picUrl
    
    @property
    def hasUser(self):
        #with Acquire(self.lock):
            return self.client.hasUser and self._1hasUser and not self.blocked
    
    @hasUser.setter
    def hasUser(self, value):
        pass
    
    @property
    def _1hasUser(self):
        #with Acquire(self.lock):
            return not IsEmpty(self.mid)
    
    @_1hasUser.setter
    def _1hasUser(self, value):
        pass
    
    @property
    def time(self):
        return self._1profile.time
    
    @time.setter
    def time(self, value):
        with Acquire(self.oLock, self._1profile.lock):
            self._1profile.time = value
            
    @property
    def profile(self):
        if self.shouldGetObj:
            return self.GetProfile()
        if not self.time and self.hasUser:
            with self.objCond:
                if not self.time:
                    while self.gettingObj:
                        self.objCond.wait(1)
                    if self.shouldGetObj:
                        return self.GetProfile()
        return self._1profile
    
    @profile.setter
    def profile(self, value):
        with Acquire(self.lock, self.oLock):
            self._1profile = value
            
        
    @property
    def name(self):
        if self.shouldGetObj:
            return self.GetName()
        name = self.profile.name
        if (not self.time or not name) and self.hasUser:
            return self.GetName()
        return name
    
    @name.setter
    def name(self, value):
        with Acquire(self.oLock, self._1profile.lock):
            self._1profile.name = value
    
    def GetProfile(self):
        if self.AskMayGetObj():
            return self.client.GetProfile(self)
        with self.objCond:
            while self.gettingObj:
                self.objCond.wait(1)
            if self.AskShouldGetObj():
                return self.client.GetProfile(self)
        return self._1profile
    
    
    def GetName(self):
        return self.GetProfile().name
    
    def Add(self):
        return self.client.AddUser(self)
            
    def InviteInto(self, room):
        return self.client.InviteInto(room, [self])
            
    @property
    def chatroomType(self):
        return ChatroomType.user
        
    
class Room(Chatroom):
    
    def __init__(self, id = None, client = None, mid = None, hasOA = False, hasUser = False, init = True, uId = None):
        Chatroom.__init__(self, id, client, mid)
        if hasUser is None:
            hasUser = False
        self._3id = None
        self.uLock = Lock()
        if uId:
            self._1SetUId(uId)
        else:
            self._1uId = None
        self._2hasOA = hasOA
        self._2hasUser = hasUser
        self._1members = []
        if init and self.hasUser:
            self.client.Thread(self.GetMembers)
            
    def InitRoom(self, force=False):
        if self.client.hasOA and self.client.hasUser and not (self.hasUser and self.hasOA):
            if self.key:
                if force:
                    key = self.key
                else:
                    return False
            else:
                key = randint(1000, 9999)
                while key in self.client._1waitingRoom:
                    key = randint(1000, 9999)
                key = str(key)
                self.key = key
            self.client._1waitingRoom[key] = self
            self.SendText("[INITROOM] %d %s" % (self._2id, key))
            return True
        return False
            
            
    def RemoveLink(self):
        uObj = self.uObj
        if uObj:
            uObj.rId = None
            with self.client.GetCursor() as cur:
                cur.Execute("UPDATE Users SET rId=NULL WHERE id=%s", (uObj._2id,))
                cur.Commit()
        self.uId = None
        with self.client.GetCursor() as cur:
            cur.Execute("UPDATE ChatRooms SET uId=NULL WHERE id=%s", (self._2id,))
            cur.Commit()
            
    @property
    def rId(self):
        if self.hasOA:
            return self._2id

    @property
    def rObj(self):
        if self.hasOA:
            return self
            
    
    @property
    def _2id(self):
        with Acquire(self.lock, self.uLock):
            return self._3id
    
    @_2id.setter
    def _2id(self, value):
        with Acquire(self.lock, self.uLock):
            self._3id = value
            u = self.uObj
            if u is not None and u._1uId is None:
                u.uId = value
            
    @property
    def uObj(self):
        with Acquire(self.uLock):
            if self._1uId:
                return self.client.GetObjByRId(self._1uId)

    @uObj.setter
    def uObj(self, value):
        if value is None:
            self.uId = None
            return
        if not isinstance(value, User):
            raise Exception("Expected User type")
        self.uId = value._2id

        
    @property
    def uId(self):
        with Acquire(self.uLock):
            return self._1uId
    
    @uId.setter
    def uId(self, value):
        with Acquire(self.uLock):
            if value != self._1uId:
                self._1SetUId(value)
            
    def _1SetUId(self, value):
        with Acquire(self.uLock, self.client.lock):
            if self._1uId != value:
                self._1uId = value
                with self.client.GetCursor() as cur:
                    if self.mid:
                        cur.Execute("UPDATE ChatRooms SET uId=%s WHERE id=%s OR lineMid=%s", (value, self._2id, self.mid))
                    else:
                        cur.Execute("UPDATE ChatRooms SET uId=%s WHERE id=%s OR lineId=%s", (value, self._2id, self.id))
                    cur.Commit()
    @property
    def members(self):
        if self.shouldGetObj:
            return self.GetMembers()
        if not self.time and self.hasUser:
            with self.objCond:
                if not self.time:
                    while self.gettingObj:
                        self.objCond.wait(1)
                    if self.shouldGetObj:
                        return self.GetMembers()
        return [self.client.userClient._1GetObjByLineMid(x) for x in self._1members]
    
    @members.setter
    def members(self, value):
        with Acquire(self.oLock):
            self.time = time()
            self._1members = value
            
    def _1SetObjAndTime(self, obj, t = None):
        with Acquire(self.oLock):
            if t is None:
                t = time()
            self.time = t
        members0 = obj.contacts
        members = None
        if members0 and len(members0) > 0:
            members = [self.client.userClient._1GetObjByLineMid(x.mid, obj=x, time=t) for x in members0]
        if members:
            with Acquire(self.oLock):
                self.members = [x.mid for x in members]
        self.gettingObj = False
        
    def GetMembers(self):
        if self.AskMayGetObj():
            return self.client.GetMembers(self)
        with self.objCond:
            while self.gettingObj:
                self.objCond.wait(1)
            if self.AskShouldGetObj():
                return self.client.GetMembers(self)
        return [self.client.userClient._1GetObjByLineMid(x) for x in self._1members]
        
    def Refresh(self):
        return len(self.GetMembers()) > 0
    
    def Leave(self):
        if not self.hasUser:
            return False
        #TODO : Kick OA
        return self.client.Leave(self)
    
    def Invite(self, users):
        if not isinstance(users, list):
            return self.client.InviteInto(self, users)
        
    def TrySync(self):
        if self.mid and self.client.hasUser and not self.hasUser:
            return self.Sync()
        elif self.id and self.client.hasOA and not self.hasOA:
            return self.Sync()
        
    def Sync(self, obj2 = None):
        if obj2 is None:
            obja = None
            if self.client.hasOA and (not IsEmpty(self.id)) and self.id in self.client._1objectsByLineId:
                obja = self.client._1objectsByLineId[self.id]
            objb = None
            if self.client.hasUser and (not IsEmpty(self.mid)) and self.mid in self.client._1objectsByLineMid:
                objb = self.client._1objectsByLineMid[self.mid]
            if obja is self:
                obj2 = objb
            else:
                obj2 = obja
        if obj2 is self:
            return self
        if obj2 is not None:
            if self.chatroomType != obj2.chatroomType or not isinstance(obj2, Room):
                raise Exception("[Sync] self and obj2 is not of the same type. id='%s', mid='%s'" % (self.id or obj2.id, self.mid or obj2.mid))
            with Acquire(self.lock, obj2.lock, self.oLock, obj2.oLock, self.uLock, obj2.uLock):
                if not IsEmpty(self.id):
                    obj2.id = self.id
                elif not IsEmpty(obj2.id):
                    self.id = obj2.id
                if not IsEmpty(self.mid):
                    obj2.mid = self.mid
                elif not IsEmpty(obj2.mid):
                    self.mid = obj2.mid
                hasOA = self._2hasOA or obj2._2hasOA
                self.hasOA = hasOA
                obj2.hasOA = hasOA
                self._1hasOA = hasOA
                obj2._1hasOA = hasOA
                self._2hasOA = hasOA
                obj2._2hasOA = hasOA
                hasUser = self._2hasUser or obj2._2hasUser
                self.hasUser = hasUser
                obj2.hasUser = hasUser
                self._1hasUser = hasUser
                obj2._1hasUser = hasUser
                self._2hasUser = hasUser
                obj2._2hasUser = hasUser
                if self.chatroomType == ChatroomType.room:
                    try:
                        with Acquire(self.client.lock):
                            self.client.rooms.remove(obj2)
                    except Exception:
                        pass
                else:
                    try:
                        with Acquire(self.client.lock):
                            self.client.groups.remove(obj2)
                    except Exception:
                        pass
                with Acquire(self.uLock, obj2.uLock):
                    if self.uId:
                        obj2.uId = self.uId
                        u = obj2.uObj
                        if u:
                            u.rObj = self
                    elif obj2.uId:
                        self.uId = obj2.uId
                        u = self.uObj
                        if u:
                            u.rObj = obj2
                if self.uId:
                    with Acquire(self.client.lock):
                        self.client._1objectsByRId[self._2id] = self
                with Acquire(self.oLock, obj2.oLock):
                    if self.time < obj2.time:
                        self.time = obj2.time
                        self._1members = obj2._1members
                        if self.chatroomType == ChatroomType.group:
                            self._1invitees = obj2._1invitees
                            self._1name = obj2._1name
                    else:
                        obj2.time = self.time
                        obj2._1members = self._1members
                        if obj2.chatroomType == ChatroomType.group:
                            obj2._1invitees = self._1invitees
                            obj2._1name = self._1name

        #print("Syncing mid=%s" % self.mid)
        with Acquire(self.client.lock):
            self.client._1objectsUserByMsgId =  { k:v for k, v in self.client._1objectsUserByMsgId.items() if v is not obj2 and v is not self } 
            self.client._1objectsOAByMsgId =  { k:v for k, v in self.client._1objectsOAByMsgId.items() if v is not obj2 and v is not self } 
            self.client._1objectsByLineId[self.id] = self
            self.client._1objectsByLineMid[self.mid] = self
            if self.key and self.key in self.client._1waitingRoom:
                del self.client._1waitingRoom[self.key]
            if obj2:
                if obj2.key and obj2.key in self.client._1waitingRoom:
                    del self.client._1waitingRoom[obj2.key]
                obj2.key = None
            self.key = None
            #print("Syncing mid=%s to DB" % self.mid)
            if self.client.db is not None and not IsEmpty(self.id) and not IsEmpty(self.mid):
                with self.client.GetCursor() as cur:
                    #print("Syncing mid=%s to DB 2" % self.mid)
                    cur.Execute("SELECT id, lineId, lineMid FROM ChatRooms WHERE lineId=%s OR lineMid=%s ORDER BY hasOA", (self.id, self.mid))
                    fs = cur.FetchAll()
                    lenfs = len(fs)
                    id = None
                    if lenfs == 0:
                        #print("Syncing mid=%s to DB lenfs == 0:" % self.mid)
                        cur.Execute("INSERT INTO ChatRooms(lineId, lineMid, type, hasOA, hasUser) Values(%s,%s,%s,%s,%s) RETURNING id", (self.id, self.mid, self.chatroomType, self._2hasOA, self._2hasUser,))
                        id = cur.FetchOne()[0]
                        cur.Commit()
                    elif lenfs > 2:
                        #print("Syncing mid=%s to DB lenfs > 2" % self.mid)
                        raise Exception("LENFS > 2 HOW DID THIS EVEN HAPPEN")
                    else:
                        if lenfs == 2:
                            #print("Syncing mid=%s to DB lenfs == 2" % self.mid)
                            cur.Execute("DELETE FROM Chatrooms WHERE id=%s", (fs[1][0],))
                            cur.Commit()
                        f = fs[0]
                        id = f[0]
                        if IsEmpty(f[2]):
                            #print("Syncing mid=%s to DB IsEmpty(f[2])" % self.mid)
                            cur.Execute("UPDATE ChatRooms SET lineMid=%s, type=%s, hasOA=%s, hasUser=%s WHERE id=%s", (self.mid, self.chatroomType, self._2hasOA, self._2hasUser, id))
                            cur.Commit()
                        elif IsEmpty(f[1]):
                            #print("Syncing mid=%s to DB IsEmpty(f[1])" % self.mid)
                            cur.Execute("UPDATE ChatRooms SET lineId=%s, type=%s, hasOA=%s, hasUser=%s WHERE id=%s", (self.id, self.chatroomType, self._2hasOA, self._2hasUser, id))
                            cur.Commit()
                        else:
                            #print("Syncing mid=%s to DB f[1] and f[2] exists" % self.mid)
                            cur.Execute("UPDATE ChatRooms SET type=%s, hasOA=%s, hasUser=%s WHERE id=%s", (self.chatroomType, self._2hasOA, self._2hasUser, id))
                            cur.Commit()

                    self._2id = id
                    cur.Execute("DELETE FROM LineIdByMsgId WHERE lineId=%s", (self.id,))
                    cur.Commit()
                    cur.Execute("DELETE FROM LineMidByMsgId WHERE lineMid=%s", (self.mid,))
                    cur.Commit()
                    

    @property
    def hasUser(self):
        #with Acquire(self.lock):
            return self.client.hasUser and self._1hasUser
    
    @hasUser.setter
    def hasUser(self, value):
        if self._2hasUser != value:
            with Acquire(self.lock, self.client.lock):
                if self._2hasUser != value:
                    self._2hasUser = value
                    if self.client.db is not None:
                        with self.client.GetCursor() as cur:
                            cur.Execute("UPDATE ChatRooms SET hasUser=%s WHERE lineId=%s OR lineMid=%s", (self._2hasUser, self.id, self.mid))
                            cur.Commit()
                if self._1hasUser != value:
                    self._1hasUser = value
                    
    @property
    def hasOA(self):
        #with Acquire(self.lock):
            return self.client.hasOA and self._1hasOA
    
    @hasOA.setter
    def hasOA(self, value):
        if self._2hasOA != value:
            with Acquire(self.lock, self.client.lock):
                if self._2hasOA != value:
                    self._2hasOA = value
                    if self.id is not None and self.mid is not None and self.client.db is not None:
                        with self.client.GetCursor() as cur:
                            cur.Execute("UPDATE ChatRooms SET hasOA=%s WHERE lineId=%s OR lineMid=%s", (self._2hasOA, self.id, self.mid))
                            cur.Commit()
                if self._1hasOA != value:
                    self._1hasOA = value
            
    @property
    def chatroomType(self):
        return ChatroomType.room
    
class Group(Room):
    def __init__(self, id = None, client = None, mid = None, hasOA = False, hasUser = False, init = True):
        Room.__init__(self, id, client, mid, hasOA, hasUser, init=False, uId=None)
        self._1invitees = []
        self.creator = None
        if init and self.hasUser:
            self.client.Thread(self.GetInvitees)
            
    @property
    def chatroomType(self):
        return ChatroomType.group
    
    @property
    def uId(self):
        return None
    
    @uId.setter
    def uId(self, value):
        pass
    
    @property
    def uObj(self):
        return None
            
    @property
    def invitees(self):
        if self.shouldGetObj:
            return self.GetInvitees()
        if not self.time and self.hasUser:
            with self.objCond:
                if not self.time:
                    while self.gettingObj:
                        self.objCond.wait(1)
                    if self.shouldGetObj:
                        return self.GetInvitees()
        return [self.client.userClient._1GetObjByLineMid(x) for x in self._1invitees]
    
    @invitees.setter
    def invitees(self, value):
        with Acquire(self.oLock):
            self.time = time()
            self._1invitees = value
            
    def _1SetObjAndTime(self, obj, t=None):
        start = time()
        with Acquire(self.oLock):
            if t is None:
                t = time()
            self.time = t
            self.name = obj.name
        creator0 = obj.creator
        creator = None
        if creator0:
            try:
                creator = self.client.userClient._1GetObjByLineMid(creator0.mid, obj = creator0, time=t)
            except Exception:
                pass
        if creator:
            with Acquire(self.oLock):
                self.creator = creator
        members0 = obj.members
        members = None
        if members0 and len(members0) > 0:
            members = [self.client.userClient._1GetObjByLineMid(x.mid, obj=x, time=t) for x in members0]
        invitees0 = obj.invitee
        invitees = None
        if invitees0 and len(invitees0) > 0:
            try:
                invitees = [self.client.userClient._1GetObjByLineMid(x.mid, obj=x, time=t) for x in invitees0]
            except TypeError:
                pass
        if members or invitees:
            with Acquire(self.oLock):
                if members:
                    self.members = [x.mid for x in members]
                if invitees:
                    self.invitees = [x.mid for x in invitees]
        self.gettingObj = False
            
    @property
    def name(self):
        if self.shouldGetObj:
            return self.GetName()
        if (not self.time or not self._1name) and self.hasUser:
            with self.objCond:
                if not self.time:
                    while self.gettingObj:
                        self.objCond.wait(1)
                    if self.shouldGetObj:
                        return self.GetName()
        return self._1name
    
    @name.setter
    def name(self, value):
        with Acquire(self.oLock):
            self._1time = time()
            self._1name = value
        
    def GetName(self):
        return self.client.GetGroupName(self)
        
    def GetInvitees(self):
        if self.AskMayGetObj():
            return self.client.GetGroupInvitees(self)
        with self.objCond:
            while self.gettingObj:
                self.objCond.wait(1)
            if self.AskShouldGetObj():
                return self.client.GetGroupInvitees(self)
        return self._1invitees
    
    def Kick(self, users=[]):
        return self.client.KickFromGroup(self, users)
    
    def Join(self):
        if not self.client.JoinGroup(self):
            return False
        self.hasUser = True
        return True
    
    
        
        
    
class Profile(object):
    def __init__(self):
        self.lock = Lock()
        self._1name = None
        self._1status = None
        self._1statusMessage = None
        self._1picUrl = None
        self._1relation = None
        self._1status = None
        self._1capableBuddy = None
        self._1userType = None
        self.type = Type.profile
        self.time = 0
        
    @property
    def blocked(self):
        return self._1status is not None and int(self._1status) > 0 and int(self._1status)%2 == 0
    
    @property
    def isOA(self):
        return self._1type is not None and self._1type == UserType.promotionBot
        
    @property
    def userType(self):
        return self._1userType
        
    @property
    def name(self):
        return self._1name
    
    @name.setter
    def name(self, value):
        self.time = time()
        self._1name = value
        
    @property
    def status(self):
        return self._1status
    
    @status.setter
    def status(self, value):
        self.time = time()
        try:
            self._1status = int(value)
        except Exception:
            pass
        
    @property
    def picUrl(self):
        return self._1picUrl
    
    @picUrl.setter
    def picUrl(self, value):
        self.time = time()
        self._1picUrl = value
        
    @property
    def relation(self):
        return self._1relation
    
    @relation.setter
    def relation(self, value):
        self.time = time()
        try:
            self._1relation = int(value)
        except Exception:
            pass
        
    @property
    def statusMessage(self):
        return self._1statusMessage
    
    @statusMessage.setter
    def statusMessage(self, value):
        self.time = time()
        self._1statusMessage = value
        
    @property
    def capableBuddy(self):
        return self._1capableBuddy
    
    @capableBuddy.setter
    def capableBuddy(self, value):
        self.time = time()
        try:
            self._1capableBuddy = bool(value)
        except Exception:
            pass
    
class ChatroomMember(object):
    def __init__(self, chatroom, member):
        self.chatroom = chatroom
        self.member = member
        
    def __ne__(self, other):
        return self is not other or not isinstance(other, ChatroomMember) or self.chatroom != other.chatroom or self.member != other.member
        
    def __eq__(self, other):
        return not self.__ne__(other)
    
    def _2hash__(self):
        return hash(str(self.chatroom._2hash__()) + str(self.member._2hash__()))
    
    