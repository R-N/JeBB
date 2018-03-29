from line2.models.command import ContinuousTextCommand, Parameter, ParameterType, CommandResultType, CommandResult, CommandContinuousCallType
from line2.models.types import Rule
from line2.utils import IsEmpty
from random import choice

def Get(x):
    if isinstance(x, list):
        return Get(choice(x))
    return x

class CompoundExactReply(object):
    def __init__(self, exactStart=None, exactEnd=None, exactWordIns=None, exactWordInRule = Rule.And, exactIns=None, exactInRule = Rule.And, replies=[]):
        if IsEmpty(replies):
            raise Exception("Replies can't be empty")
        if IsEmpty(exactStart):
            self.exactStart = None
        else:
            self.exactStart = exactStart
        if IsEmpty(exactEnd):
            self.exactEnd = None
        else:
            self.exactEnd = exactEnd
        if IsEmpty(exactWordIn):
            self.exactWordIns = None
        else:
            if isinstance(exactWordIns, str):
                self.exactWordIns = [exactWordIns]
            else:
                self.exactWordIns = exactWordIns
        if exactWordInRule not in Rule.All:
            raise Exception("Invalid exactWordInRule : " + str(exactWordInRule))
        self.exactWordInRule = exactWordInRule
        if IsEmpty(exactIns):
            self.exactIns = None
        else:
            if isinstance(exactIns, str):
                self.exactIns = [exactIns]
            else:
                self.exactIns = exactIns
        if exactInRule not in Rule.All:
            raise Exception("Invalid exactInRule : " + str(exactInRule))
        self.exactInRule = exactInRule
            
    def Reply(self, text):
        if self.exactStart:
            if not text.startswith(self.exactStart):
                return
        if self.exactEnd:
            if not text.endswith(self.exactEnd):
                return
        if self.exactWordIns:
            words = {x:0 for x in text.split(' ')}
            words2 = {x.strip('.,/;\'\\<>?:"{}|!@#$%^&*()_+=-~`'):0 for x in words.iterkeys()}
            words3 = {x.strip('123457890'):0 for x in words2.iterkeys()}
            if self.exactWordInRule == Rule.And:
                for x in self.exactWordIns:
                    if x not in words and x not in words2 and x not in words3:
                        return
            elif self.exactWordInRule == Rule.Or:
                for x in self.exactWordIns:
                    if x in words or x in words2 or x in words3:
                        break
        if self.exactIns:
            if self.exactWordInRule == Rule.And:
                for x in self.exactIns:
                    if x not in text:
                        return
            elif self.exactWordInRule == Rule.Or:
                for x in self.exactIns:
                    if x in text:
                        break
        return CommandResult(texts=[Get(self.replies)])
        
exactCompound = [
    
]
        
exact = {
    'hello':['Hi there!']
}

exactStart = [
    ('yeah', ['Hell yeah'])
]

exactEnd = [
    ('?', ['idk', 'perhaps', 'nope', 'yeah', 'ask again'])
]

exactWordIn = [
    ('bad', ['Real bad'])
]

exactIn = [
    ('good', ['Nice'])
]

exactReplace = [
    ('nano', ['Hakase'])
]

exactCompoundRoom = {}
exactRoom = {}
exactStartRoom = {}
exactEndRoom = {}
exactWordInRoom = {}
exactInRoom = {}
exactReplaceRoom = {}

exactCompoundSender = {}
exactSender = {}
exactStartSender = {}
exactEndSender = {}
exactWordInSender = {}
exactInSender = {}
exactReplaceSender = {}


roomDictionary = {
    'exactcompound':(exactCompoundRoom, list),
    'exact':(exactRoom, dict),
    'exactstart':(exactStartRoom, list),
    'exactend':(exactEndRoom, list),
    'exactwordin':(exactWordInRoom, list),
    'exactin':(exactInRoom, list),
    'exactreplace':(exactReplaceRoom, list),
}

senderDictionary = {
    'exactcompound':(exactCompoundSender, list),
    'exact':(exactSender, dict),
    'exactstart':(exactStartSender, list),
    'exactend':(exactEndSender, list), 
    'exactwordin':(exactWordInSender, list), 
    'exactin':(exactInSender, list), 
    'exactreplace':(exactReplaceSender, list),
}

def _1On(chatroom, sender, mode, name, on=True):
    if name in roomDictionary:
        if mode==0 or mode==1:
            d = roomDictionary[name]
            if chatroom in d[0]:
                d[0][chatroom][0] = on
            else:
                d[0][chatroom] = [on, d[1]()]
        if mode==0 or mode==2:
            d = senderDictionary[name]
            if sender in d[0]:
                d[0][sender][0] = on
            else:
                d[0][sender] = [on, d[1]()]
        return True
    return False
                
    
oned = 'turned on'
offed = 'turned off'
thisroom = 'this room'

completeArg = 'exactcompound exact exactstart exactend exactwordin exactin exactreplace'
splitCompleteArg = completeArg.split(' ')

def On(chatroom, sender, options, text, on=True):
    text = text.lower()
    toOns = text.split(' ')
    mode = 0
    on0 = toOns[0]
    if on0 == 'room':
        mode = 1
        toOns.pop(0)
    elif 'r' in options:
        mode=1
    elif on0 == 'sender':
        mode = 2
        toOns.pop(0)
    elif 's' in options:
        mode=2
    if len(toOns) == 0:
        toOns = splitCompleteArg
    oneds = []
    for toA in toOns:
        if _1On(chatroom, sender, mode, toA, on):
            oneds.append(toA)
    onee = ''
    if mode == 0:
        name = sender.name
        if name:
            onee = 'this room and ' + name
        else:
            onee = 'this room and you'
    elif mode==1:
        onee = thisroom
    elif mode==2:
        name = sender.name
        if name:
            onee = name
        else:
            onee = "you"
    if on:
        sOn = oned
    else:
        sOn = offed
    if len(oneds) > 0:
        return '%s reply has been %s for %s' % (', '.join(oneds), sOn, onee)
    return None

def _1ExactCompound(l, text):
    for ecr in l:
        ret = ecr.Reply(text)
        if ret:
            return ret

def _1Exact(dictionary, text):
    if text in dictionary:
        return CommandResult(texts=[Get(dictionary[text])])

def _1ExactStart(l, text):
    for kv in l:
        if text.startswith(kv[0]):
            return CommandResult(texts=[Get(kv[1])])
        
def _1ExactEnd(l, text):
    for kv in l:
        if text.endswith(kv[0]):
            return CommandResult(texts=[Get(kv[1])])
    
def _1ExactWordIn(l, text):
    words = {x:0 for x in text.split(' ')}
    words2 = {x.strip('.,/;\'\\<>?:"{}|!@#$%^&*()_+=-~`'):0 for x in words.iterkeys()}
    words3 = {x.strip('123457890'):0 for x in words2.iterkeys()}
    for kv in l:
        key = kv[0]
        if key in words or key in words2 or key in words3:
            return CommandResult(texts=[Get(kv[1])])
        
def _1ExactIn(l, text):
    for kv in l:
        if kv[0] in text:
            return CommandResult(texts=[Get(kv[1])])
        
def _1ExactReplace(l, text):
    exactReplaced = False
    for kv in l:
        word = kv[0]
        if not exactReplaced and word in text:
            exactReplaced=True
        text = text.replace(word, Get(kv[1]))
    if exactReplaced:
        return CommandResult(texts=[text])

replyList=[
    (exactCompound, exactCompoundRoom, exactCompoundSender, _1ExactCompound),
    (exact, exactRoom, exactSender, _1Exact),
    (exactStart, exactStartRoom, exactStartSender, _1ExactStart),
    (exactEnd, exactEndRoom, exactEndSender, _1ExactEnd),
    (exactWordIn, exactWordInRoom, exactWordInSender, _1ExactWordIn),
    (exactIn, exactInRoom, exactInSender, _1ExactIn),
    (exactReplace, exactReplaceRoom, exactReplaceSender, _1ExactReplace),
]
        
def _1HandleExactReply(chatroom, sender, text, tup):
    roomDict = tup[1]
    senderDict = tup[2]
    hasSender = sender in senderDict and senderDict[sender][0]
    if hasSender or (sender not in senderDict and chatroom in roomDict and roomDict[chatroom][0]):
        if sender in senderDict:
            ds = senderDict[sender]
            if ds[0]:
                ret = tup[3](ds[1], text)
                if ret:
                    return ret
        if chatroom in roomDict:
            dr = roomDict[chatroom]
            if dr[0]:
                ret = tup[3](dr[1], text)
                if ret:
                    return ret
        return tup[3](tup[0], text)

def HandleExactReply(message, options='', text='', continuous=CommandContinuousCallType.notContinuous, on='', off='', word='', replies=''):
    text=text.lower()
    if continuous:
        chatroom = message.chatroom
        sender = message.sender
        for tup in replyList:
            ret = _1HandleExactReply(chatroom, sender, text, tup)
            if ret:
                return ret
        return CommandResult.Failed()
    else:
        if text == 'on':
            on = completeArg
        elif text=='off':
            off = completeArg
        ret = []
        if not IsEmpty(on):
            a = (On(message.chatroom, message.sender, options, on, True))
            if a:
                ret.append(a)
        if not IsEmpty(off):
            d = (On(message.chatroom, message.sender, options, off, False))
            if d:
                ret.append(d)
        if IsEmpty(ret):
            raise Exception('Invalid parameters')
        return CommandResult(texts=ret)

def Init(client):
    pass

exactReplyCmd = ContinuousTextCommand(
    'exactreply',
    HandleExactReply,
    desc='Replies if word found.',
    initFunction = Init
)