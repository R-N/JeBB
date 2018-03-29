

from line2.models.command import HybridCommand, Parameter, ParameterType, CommandResultType, CommandResult
from random import randint
from line2.utils import IsEmpty, Lock
from requests import Session as RequestsSession, get as RequestsGet, post as RequestsPost
from json import loads
from line2.models.types import ChatroomType
from line2.models.chatrooms import User, Room, Group
from line2.models.content import Image

    
global lock
lock = Lock()

global builtinTemplates
builtinTemplates = {}
global builtinTemplateCount
builtinTemplateCount = 0
global builtinTemplateNames
builtinTemplateNames = []
global builtinTemplatesByDesc
builtinTemplatesByDesc = []

def IsEmpty2(s):
    return IsEmpty(s.replace('_', ''))

def GetBuiltinTemplates():
    try:
        r = RequestsGet("https://memegen.link/api/templates/")
        sTemplates = r.text.replace("https://memegen.link/api/templates/", '')
        global lock
        with lock:
            global builtinTemplates
            builtinTemplates = {v:k for k, v in loads(sTemplates).iteritems()}
            global builtinTemplateNames
            builtinTemplateNames = [x for x in builtinTemplates.iterkeys()]
            global builtinTemplateCount
            builtinTemplateCount = len(builtinTemplates)
            global builtinTemplatesByDesc
            builtinTemplatesByDesc = sorted([(v,k) for k,v in builtinTemplates.iteritems()])
    except Exception:
        pass

def SendTemplateList(chatroom, sender):
    GetBuiltinTemplates()
    ret = []
    s2Templates = ['Builtin Templates :']
    global builtinTemplatesByDesc
    for kv in builtinTemplatesByDesc:
        si = '\n' + kv[0] + ' : ' + kv[1]
        s2 = s2Templates[-1] + si
        if len(s2) > 2000:
            s2Templates.append('Builtin Templates :' + si)
        else:
            s2Templates[-1] = s2
    ret = ret + s2Templates
    #for s2 in s2Templates:
    #    chatroom.SendText(s2)

    global customTemplateCount
    if customTemplateCount > 0:
        s2Templates = ['Global Custom Templates :']
        global customTemplatesByDesc
        for kv in customTemplatesByDesc:
            desc = kv[0]
            if IsEmpty(desc):
                desc = 'No description'
            print("desc '%s' kv1 '%s'" % (str(desc), str(kv[1])))
            si = '\n' + desc + ' : ' + kv[1]
            s2 = s2Templates[-1] + si
            if len(s2) > 2000:
                s2Templates.append('Global Custom Templates :' + si)
            else:
                s2Templates[-1] = s2
        
        #for s2 in s2Templates:
        #    chatroom.SendText(s2)
        ret = ret + s2Templates

    if chatroom.chatroomType != ChatroomType.user:
        global roomCustomTemplates
        rId = chatroom._2id
        if rId is not None and rId in roomCustomTemplates:
            roomTemplates = roomCustomTemplates[rId]
            if roomTemplates.count > 0:
                s2Templates = ['Room Custom Templates :']
                for kv in roomTemplates.byDesc:
                    desc = kv[0]
                    if IsEmpty(desc):
                        desc = 'No description'
                    si = '\n' + desc + ' : ' + kv[1]
                    s2 = s2Templates[-1] + si
                    if len(s2) > 2000:
                        s2Templates.append('Room Custom Templates :' + si)
                    else:
                        s2Templates[-1] = s2

                #for s2 in s2Templates:
                #    chatroom.SendText(s2)
                ret = ret + s2Templates

    if sender is not None:
        global userCustomTemplates
        uId = sender._2id
        if uId is not None and uId in userCustomTemplates:
            userTemplates = userCustomTemplates[uId]
            if userTemplates.count > 0:
                s2Templates = ['User Custom Templates :']
                for kv in userTemplates.byDesc:
                    desc = kv[0]
                    if IsEmpty(desc):
                        desc = 'No description'
                    si = '\n' + desc + ' : ' + kv[1]
                    s2 = s2Templates[-1] + si
                    if len(s2) > 2000:
                        s2Templates.append('User Custom Templates :' + si)
                    else:
                        s2Templates[-1] = s2

                #for s2 in s2Templates:
                #    chatroom.SendText(s2)
                ret = ret + s2Templates
    return CommandResult(texts=ret)

def Escape(s):
    if IsEmpty2(s):
        return '_'
    return s.replace('-', '--').replace('_', '__').replace(' ', '-').replace('?', '~q').replace('%', '~p').replace('#', '~h').replace('/', '~s').replace('"', "''")

def GetUrl(name='blb', top='_', bot='_', font='impact', img=None):
    memeUrl = "memegen.link/" + name + "/" + top + "/" + bot + ".jpg?font=" + font
    if not IsEmpty(img):
        memeUrl = memeUrl + "&alt=" + img
    return memeUrl

def Send(chatroom, sender=None, name='random', top='_', bot='_', font='impact', img=''):
    if name=='random':
        rand = GetRandomTemplate(chatroom, sender)
        name = rand[0]
        img = rand[1]
    elif name == "custom":
        if IsEmpty(img):
            raise Exception("img is empty")
    else:
        if IsEmpty(img):
            img = GetImg(chatroom, sender, name)
        if IsEmpty(img):
            if name not in builtinTemplates:
                chatroom.SendText("[Command(Meme)] Template named '" + name + "' not found")
                return CommandResult.Done()
        else:
            name = "custom"

    top = Escape(top)
    bot = Escape(bot)
    if IsEmpty2(top) and IsEmpty2(bot) and not IsEmpty(img):
        return CommandResult(images=Image(client=chatroom.client, url=img))
    url = GetUrl(name, top, bot, font, img)
    return CommandResult(images=Image(client=chatroom.client, url="https://" + url))

def RegisterMeme(message, options, name, desc=None, mode=None, images=None, params=None, insert=True):
    if insert:
        cur = message.client.GetCursor()
    url = images[0].imgurUrl
    opening = ""
    if mode == 10:
        if insert:
            cur.Execute("INSERT INTO CustomMemes(name, imageUrl, deactivationDatetime, description) VALUES(%s, %s, NULL, %s) ON CONFLICT(name) DO UPDATE SET imageUrl=EXCLUDED.imageUrl, deactivationDatetime=NULL, description=EXCLUDED.description", (name, url, desc))
        opening = "Global"
        global lock
        with lock:
            global customTemplates
            customTemplates[name] = (url, desc)
            global customTemplateNames
            if name in customTemplateNames:
                global customTemplatesByDesc
                for kv in customTemplatesByDesc:
                    if kv[1] == name:
                        kv[0] = desc
            else:
                customTemplateNames.append(name)
                global customTemplateCount
                customTemplateCount+=1
                global customTemplatesByDesc
                customTemplatesByDesc.append([desc, name])
    ls = []
    if mode == 0 or mode == 1:
        if insert:
            cur.Execute("INSERT INTO RoomCustomMemes(rId, name, imageUrl, deactivationDatetime, description) VALUES(%s, %s, %s, NULL, %s) ON CONFLICT(rId, name) DO UPDATE SET imageUrl=EXCLUDED.imageUrl, deactivationDatetime=NULL, description=EXCLUDED.description", (message.chatroom._2id, name, url, desc))
        global lock
        with lock:
            global roomCustomTemplates 
            rId = message.chatroom._2id
            if rId not in roomCustomTemplates:
                roomCustomTemplates[rId] = CustomTemplate()
            l = roomCustomTemplates[rId]
            l.rId = rId
            ls.append(l)
    if mode == 0 or mode == 2:
        if insert:
            cur.Execute("INSERT INTO UserCustomMemes(uId, name, imageUrl, deactivationDatetime, description) VALUES(%s, %s, %s, NULL, %s) ON CONFLICT(uId, name) DO UPDATE SET imageUrl=EXCLUDED.imageUrl, deactivationDatetime=NULL, description=EXCLUDED.description", (message.sender._2id, name, url, desc))
        global lock
        with lock:
            global userCustomTemplates 
            uId = message.sender._2id
            if uId not in userCustomTemplates:
                userCustomTemplates[uId] = CustomTemplate()
            l = userCustomTemplates[uId]
            l.uId = uId
            ls.append(l)
    if mode < 10:
        for l in ls:
            with l.lock:
                l.templates[name] = (url, desc)
                if name in l.names:
                    for kv in l.byDesc:
                        if kv[1] == name:
                            kv[0] = desc
                else:
                    l.count+=1
                    l.names.append(name)
                    l.byDesc.append([desc, name])
                    l.byDesc.sort()
    if insert:
        cur.Commit()
    if mode == 0:
        opening = "Room and user"
    elif mode == 1:
        opening = "Room"
    elif mode == 2:
        opening = "User"
    if insert:
        closing = "registered"
    else:
        closing = "activated"
    return Send(message.chatroom, sender=message.sender, name="custom", top="%s meme template '%s'" % (opening, name), bot="Has been successfully %s" % closing, img=url)
        

def NewMeme(message, options, name, desc=None, mode=None, admin=False, images=None, params=None):
    if mode is None:
        if admin:
            mode = 10
        else:
            mode = 0
            if 'r' in options:
                mode = 1
            elif 's' in options:
                mode = 2
        if params:
            params['mode'] = mode
    if not IsEmpty(images):
        return RegisterMeme(message, options, name, desc, mode, images, params)
    if 'f' not in options:
        cur = message.client.GetCursor()
        if mode == 10:
            cur.Execute('SELECT TRUE FROM CustomMemes WHERE name=%s', (name,))
            if cur.rowCount > 0:
                message.ReplyText("[Command(Meme)] Global template named '%s' already exists. If you want to replace, please also provide the 'f' (force) option" % name)
                return CommandResult.Done()
        roomMemeExists = False
        if mode == 0 or mode==1:
            cur.Execute('SELECT TRUE FROM RoomCustomMemes WHERE name=%s AND rId=%s', (name, message.chatroom._2id))
            if cur.rowCount > 0:
                if mode == 0:
                    roomMemeExists = True
                else:
                    message.ReplyText("[Command(Meme)] Room template named '%s' already exists. If you want to replace, please also provide the 'f' (force) option" % name)
                    return CommandResult.Done()
        userMemeExists = 0
        if not message.sender:
            userMemeExists=2
        elif mode == 0 or mode == 2:
            cur.Execute('SELECT TRUE FROM UserCustomMemes WHERE name=%s AND uId=%s', (name, message.sender._2id))
            if cur.rowCount > 0:
                if mode == 0:
                    userMemeExists = 1
                else:
                    message.ReplyText("[Command(Meme)] User template named '%s' already exists. If you want to replace, please also provide the 'f' (force) option" % name)
                    return CommandResult.Done()
        if mode == 0:
            if roomMemeExists:
                if userMemeExists == 2:
                    message.ReplyText("[Command(Meme)] Room template named '%s' already exists. We can't identify you so user template is also not possible. If you want to replace, please also provide the 'f' (force) option" % name)
                    return CommandResult.Done()
                elif userMemeExists == 1:
                    message.ReplyText("[Command(Meme)] Room template and user template named '%s' already exists. If you want to replace, please also provide the 'f' (force) option" % name)
                    return CommandResult.Done()
                elif userMemeExists == 0:
                    message.ReplyText("[Command(Meme)] Room template named '%s' already exists. This way, only user template will be registered. If you want to replace the room template too, please also provide the 'f' (force) option" % name)
                    mode = 2
            else:
                if userMemeExists == 2:
                    message.ReplyText("[Command(Meme)] We can't identify you so user template is not possible. This way, only user template will be registered.")
                    mode = 1
                elif userMemeExists == 1:
                    message.ReplyText("[Command(Meme)] User template named '%s' already exists. This way, only the room template will be registered. If you want to replace, please also provide the 'f' (force) option" % name)
                    mode = 1
        if params:
            params['mode'] = mode
    return CommandResult.ExpectImage()
                
                    
invalidNames = {'new':0, 'random':0, 'custom':0, 'activate':0, 'deactivate':0}

def _1Deactivate(message, name, f, fr, fs):
    opening = ""
    if f:
        opening = "Global"
        global lock
        with lock:
            global customTemplates
            if name in customTemplates:
                desc = customTemplates[name][1]
                del customTemplates[name]
                global customTemplateNames
                customTemplateNames.remove(name)
                tup = (desc, name)
                global customTemplatesByDesc
                customTemplatesByDesc.remove(tup)
                global customTemplateCount
                customTemplateCount-=1
            
    ls = []
    if fr:
        global lock
        with lock:
            global roomCustomTemplates 
            rId = message.chatroom._2id
            if rId in roomCustomTemplates:
                roomCustomTemplates[rId] = CustomTemplate()
                l = roomCustomTemplates[rId]
                ls.append(l)
    if fs:
        global lock
        with lock:
            global userCustomTemplates 
            uId = message.sender._2id
            if uId not in userCustomTemplates:
                userCustomTemplates[uId] = CustomTemplate()
                l = userCustomTemplates[uId]
                ls.append(l)
    if not f:
        for l in ls:
            with l.lock:
                if name in l.templates:
                    desc = l.templates[name][1]
                    del l.templates[name]
                    l.names.remove(name)
                    tup = (desc, name)
                    l.byDesc.remove(tup)
                    l.count-=1
    if fr and fs:
        opening = "Room and user"
    elif fr:
        opening = "Room"
    elif fs:
        opening = "User"
    return message.ReplyText(texts=["%s meme template '%s' has been successfully deactivated" % (opening, name)])
        

def _1Activate(message, name, fr, fs):
    if fr:
        if fs:
            rUrl = fr[0]
            rDesc = fr[1]
            sUrl = fs[0]
            sDesc = fs[1]
            if rUrl == sUrl and rDesc == sDesc:
                return RegisterMeme(message, name=name, images=[Image(url=rUrl)], desc=rDesc, mode=0, options=options, insert=False)
            else:
                rRes = RegisterMeme(message, name=name, images=[Image(url=rUrl)], desc=rDesc, mode=1, options=options, insert=False)
                sRes = RegisterMeme(message, name=name, images=[Image(url=sUrl)], desc=sDesc, mode=2, options=options, insert=False)
                if rRes.images:
                    if sRes.images:
                        return CommandResult.Done(images=rRes.images + sRes.images)
                    return rRes
                elif sRes.images:
                    return sRes
                else:
                    rTexts = rRes.texts
                    sTexts = sRes.texts
                    if rTexts:
                        if sTexts:
                            return CommandResult.Done(texts=rTexts+sTexts)
                        return rRes
                    elif sTexts:
                        return sRes
                    return CommandResult.Done(texts=["Unknown Error"])
        else:
            return RegisterMeme(message, name=name, images=[Image(url=fr[0])], desc=fr[1], mode=1, options=options, insert=False)
    elif fs:
        return RegisterMeme(message, name=name, images=[Image(url=fs[0])], desc=fs[1], mode=2, options=options, insert=False)
    return CommandResult.Done()

def Activate(message, options, name, admin=False, activate=True):
    mode = 0
    if admin:
        mode = 10
    elif 'r' in options:
        mode=1
    elif 's' in options:
        mode=2
    s='a'
    if not activate:
        s='dea'
    sT = 'A'
    if not activate:
        sT='Dea'
    sDate = 'NULL'
    if not activate:
        sDate = 'NOW()'
    if not message.sender:
        if mode == 0:
            message.ReplyText("[Command(Meme)] Unfortunately we can't identify you so only room meme template named '%s' will be %sctivated if exists" % (name, s))
            mode = 1
        elif mode == 2:
            message.ReplyText("[Command(Meme)] Unfortunately we can't identify you so your request can't be fulfilled.")
            return CommandResult.Done()
    cur = message.client.GetCursor()
    f = None
    if mode == 10:
        cur.Execute("UPDATE CustomMemes SET deactivationDatetime=" + sDate + " WHERE name=%s RETURNING imageUrl, description", (name,))
        if cur.rowCount == 0:
            message.ReplyText("[Command(Meme)] %sctivating global meme template failed, template named '%s' not found" % (sT, name))
            return CommandResult.Done()
        f = cur.FetchOne()
        if activate:
            return RegisterMeme(message, name=name, images=[Image(url=f[0])], desc=f[1], mode=mode, options=options, insert=False)
    fr = None
    if mode == 0 or mode == 1:
        rId = message.chatroom._2id
        cur.Execute("UPDATE RoomCustomMemes SET deactivationDatetime=" + sDate + " WHERE rId=%s AND name=%s RETURNING imageUrl, description", (rId, name,))
        if cur.rowCount == 0:
            message.ReplyText("[Command(Meme)] %sctivating room meme template failed, template named '%s' not found" % (sT, name))
            if mode == 1:
                return CommandResult.Done()
        else:
            fr = cur.FetchOne()
            if mode == 1:
                cur.Commit()
                if activate:
                    return RegisterMeme(message, name=name, images=[Image(url=fr[0])], desc=fr[1], mode=1, options=options, insert=False)
    fs = None
    if mode == 0 or mode == 2:
        uId = message.chatroom._2id
        cur.Execute("UPDATE UserCustomMemes SET deactivationDatetime=" + sDate + " WHERE uId=%s AND name=%s RETURNING imageUrl, description", (uId, name,))
        if cur.rowCount == 0:
            message.ReplyText("[Command(Meme)] %sctivating user meme template failed, template named '%s' not found" % (sT, name))
            if mode == 2:
                return CommandResult.Done()
        else:
            fs = cur.FetchOne()
            if mode == 2:
                cur.Commit()
                if activate:
                    return RegisterMeme(message, name=name, images=[Image(url=fs[0])], desc=fs[1], mode=2, options=options, insert=False)
    cur.Commit()
    if activate:
        return _1Activate(message, name, fr, fs)
    return _1Deactivate(message, name, f, fr, fs)
        
            
            
        
        

def Meme(message, options='', text='', name=None, top=' ', bot=' ', font='impact', img=None, desc=None, images=None, admin=False, mode=None, params=None, activate=None, deactivate=None, new=None):
    if params is None:
        params = {}
    if text == 'templates':
        return SendTemplateList(message.chatroom, message.sender)
    a, b, c = text.partition(' ')
    if not IsEmpty(c):
        x = None
        if a == 'new':
            x = 'n'
        elif a == 'activate':
            x = 'a'
        elif a == 'deactivate':
            x = 'd'
        if x:
            options = options+x
            params['options'] = options
            text=c.strip()
    if activate:
        name=activate
        options = options+'a'
        params['options'] = options
    if deactivate:
        name=deactivate
        options = options+'d'
        params['options'] = options
    if new:
        name=new
        options = options+'n'
        params['options'] = options
    if 'n' in options or 'a' in options or 'd' in options:
        if IsEmpty(name):
            name=text
        if IsEmpty(name):
            message.ReplyText("[Command(Meme):New] Name can't be empty")
            return CommandResult.Done()
        if 'n' in options:
            if name in invalidNames:
                message.ReplyText("[Command(Meme):New] Name can't be '%s'" % name)
                return CommandResult.Done()
            return NewMeme(message, options, name, desc, mode, admin, images, params)
        if 'a' in options:
            return Activate(message, options, name, admin=admin)
        return Activate(message, options, name, admin=admin, activate=False)
    if name is None:
        if IsEmpty(text) or not IsEmpty2(top) or not IsEmpty2(bot) or not IsEmpty(options):
            name = 'random'
        else:
            name = text.split(' ')[0]
    if IsEmpty(name):
        chatroom.SendText("[Command(Meme)] Name can't be empty.")
        return CommandResult.Done()
    if name == 'custom':
        if IsEmpty2(top) and IsEmpty2(bot):
            message.ReplyText("[Command(Meme)] Just send the image yourself wtf")
            return CommandResult.Done()
        if IsEmpty(img):
            if images is None or len(images) == 0:
                return CommandResult.ExpectImage()
            img = images[0].imgurUrl
            if IsEmpty(img):
                message.ReplyText("Failed to reupload image.")
                return CommandResult.ExpectImage()
    return Send(message.chatroom, message.sender, name, top, bot, font, img)

GetBuiltinTemplates()

global customTemplates
customTemplates = {}
global customTemplateCount
customTemplateCount = 0
global customTemplateNames
customTemplateNames = []
global customTemplatesByDesc
customTemplatesByDesc = []

class CustomTemplate(object):
    def __init__(self):
        self.lock = Lock()
        self.uId = None
        self.rId = None
        self.templates = {}
        self.count = 0
        self.names = []
        self.byDesc = []

global roomCustomTemplates
roomCustomTemplates = {}
global userCustomTemplates
userCustomTemplates = {}

def Init(client):
    global lock
    with lock:
        GetBuiltinTemplates()
        cur = client.GetCursor()
        cur.Execute("CREATE TABLE IF NOT EXISTS CustomMemes(name TEXT UNIQUE, imageUrl TEXT, deactivationDatetime TIMESTAMP, description TEXT DEFAULT '')")
        cur.Execute("CREATE TABLE IF NOT EXISTS RoomCustomMemes(rId INTEGER, name TEXT, imageUrl TEXT, deactivationDatetime TIMESTAMP, description TEXT DEFAULT '', CONSTRAINT rMemes UNIQUE (rId, name))")
        cur.Execute("CREATE TABLE IF NOT EXISTS UserCustomMemes(uId INTEGER, name TEXT, imageUrl TEXT, deactivationDatetime TIMESTAMP, description TEXT DEFAULT '', CONSTRAINT uMemes UNIQUE (uId, name))")
        cur.Commit()
        
        cur.Execute('SELECT name, imageUrl, description FROM CustomMemes WHERE deactivationDatetime IS NULL AND imageUrl IS NOT NULL')
        global customTemplates
        customTemplates = {x[0] : (x[1], x[2]) for x in cur.FetchAll()}
        global customTemplateNames
        customTemplateNames = [x for x in customTemplates.iterkeys()]
        global customTemplateCount
        customTemplateCount = len(customTemplates)
        global customTemplatesByDesc
        customTemplatesByDesc = sorted([[v[1],k] for k, v in customTemplates.iteritems()])

        cur.Execute('SELECT name, imageUrl, description, rId FROM RoomCustomMemes WHERE deactivationDatetime IS NULL and imageUrl IS NOT NULL')
        global roomCustomTemplates 
        roomCustomTemplates = {}
        for x in cur.FetchAll():
            rId = x[3]
            if rId is None:
                continue
            name = x[0]
            if rId not in roomCustomTemplates:
                roomCustomTemplates[rId] = CustomTemplate()
            l = roomCustomTemplates[rId]
            desc = x[2]
            l.rId = rId
            l.templates[name] = (x[1], desc)
            l.count+=1
            l.names.append(name)
            l.byDesc.append([desc, name])
        for l in roomCustomTemplates.itervalues():
            print("room %s templates %s" % (str(l.rId), str(l.templates)))
            l.byDesc = sorted(l.byDesc)

        cur.Execute('SELECT name, imageUrl, description, uId FROM UserCustomMemes WHERE deactivationDatetime IS NULL and imageUrl IS NOT NULL')
        global userCustomTemplates 
        userCustomTemplates = {}
        for x in cur.FetchAll():
            uId = x[3]
            if uId is None:
                continue
            name = x[0]
            if rId not in userCustomTemplates:
                userCustomTemplates[uId] = CustomTemplate()
            l = userCustomTemplates[uId]
            desc = x[2]
            l.uId = uId
            l.templates[name] = (x[1], desc)
            l.count+=1
            l.names.append(name)
            l.byDesc.append([desc, name])
        for l in userCustomTemplates.itervalues():
            print("user %s templates %s" % (str(l.uId), str(l.templates)))
            l.byDesc = sorted(l.byDesc)
            
            
            
def GetImg(chatroom, sender, name):
    if sender is not None:
        uId = sender._2id
        global userCustomTemplates
        if uId is not None and uId in userCustomTemplates:
            userTemplates = userCustomTemplates[uId]
            if name in userTemplates.templates:
                return userTemplates.templates[name][0]
    rId = chatroom._2id
    global roomCustomTemplates
    if rId is not None and rId in roomCustomTemplates:
        roomTemplates = roomCustomTemplates[rId]
        if name in roomTemplates.templates:
            return roomTemplates.templates[name][0]
    global customTemplates
    if name in customTemplates:
        return customTemplates[name][0]
    return ''
        
def GetRandomTemplate(chatroom, sender):
    global builtinTemplateCount
    global customTemplateCount
    global userCustomTemplates
    global roomCustomTemplates
    userTemplateCount = 0
    roomTemplateCount = 0
    if sender is not None:
        uId = sender._2id
        global userCustomTemplates
        if uId is not None and uId in userCustomTemplates:
            userTemplates = userCustomTemplates[uId]
            userTemplateCount = userTemplates.count
    rId = chatroom._2id
    global roomCustomTemplates
    if rId is not None and rId in roomCustomTemplates:
        roomTemplates = roomCustomTemplates[rId]
        roomTemplateCount = roomTemplates.count
    i = randint(0, userTemplateCount + roomTemplateCount + customTemplateCount + builtinTemplateCount - 1)
    if i < userTemplateCount:
        name = userTemplate.names[i]
        return (name, userTemplates.templates[name][0])
    i -= userTemplateCount
    if i < roomTemplateCount:
        name = roomTemplate.names[i]
        return (name, roomTemplates.templates[name][0])
    i -= roomTemplateCount
    if i < customTemplateCount:
        global customTemplateNames
        name = customTemplateNames[i]
        global customTemplates
        return (name, customTemplates[name][0])
    i -= customTemplateCount
    if i < builtinTemplateCount:
        global builtinTemplateNames
        return (builtinTemplateNames[i], "")
    raise Exception("Random error, i=" + str(i))

memeCmd = HybridCommand(
    'meme',
    Meme,
    desc='Memes.',
    initFunction = Init
)
