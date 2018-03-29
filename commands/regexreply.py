from line2.models.command import ContinuousTextCommand, Parameter, ParameterType, CommandResultType, CommandResult, CommandContinuousCallType
from line2.models.types import Rule
from line2.utils import IsEmpty
from random import choice
from re import compile, subn

def Get(x):
    if isinstance(x, list):
        return Get(choice(x))
    return x
        
    
regex = [#(compiledregex, list of replies)
    
]

regexReplace = [#(regexstring, list of replies)
    
]

regexRoom = {}
regexReplaceRoom = {}

regexSender = {}
regexReplaceSender = {}

roomDictionary = {
    'regex':(regexRoom, list),
    'regexreplace':(regexReplaceRoom, list),
}

senderDictionary = {
    'regex':(regexSender, list),
    'regexreplace':(regexReplaceSender, list),
}

def _1Activate(chatroom, sender, mode, name, activate=True):
    if name in roomDictionary:
        if mode==0 or mode==1:
            d = roomDictionary[name]
            if chatroom in d[0]:
                d[0][chatroom][0] = activate
            else:
                d[0][chatroom] = [activate, d[1]()]
        if mode==0 or mode==2:
            d = senderDictionary[name]
            if sender in d[0]:
                d[0][sender][0] = activate
            else:
                d[0][sender] = [activate, d[1]()]
        return True
    return False
                
    
activated = 'activated'
deactivated = 'deactivated'
thisroom = 'this room'

completeArg = 'regex regexreplace'
splitCompleteArg = completeArg.split(' ')

def Activate(chatroom, sender, text, activate=True):
    text = text.lower()
    toActivates = text.split(' ')
    mode = 0
    activate0 = toActivates[0]
    if activate0 == 'room':
        mode = 1
        toActivates.pop(0)
    elif activate0 == 'sender':
        mode = 2
        toActivates.pop(0)
    if len(toActivates) == 0:
        toActivates = splitCompleteArg
    activateds = []
    for toA in toActivates:
        if _1Activate(chatroom, sender, mode, toA, activate):
            activateds.append(toA)
    activatee = ''
    if mode == 0:
        name = sender.name
        if name:
            activatee = 'this room and ' + name
        else:
            activatee = 'this room and you'
    elif mode==1:
        activatee = thisroom
    elif mode==2:
        name = sender.name
        if name:
            activatee = name
        else:
            activatee = "you"
    if activate:
        sActivate = activated
    else:
        sActivate = deactivated
    if len(activateds) > 0:
        return '%s reply has been %s for %s' % (', '.join(activateds), sActivate, activatee)
    return None

def _1Regex(l, text):
    for rr in l:
        m = rr[0].match(text)
        if m:
            return CommandResult(texts=[Get(rr[1])])
    
def _1RegexReplace(l, text):
    replaced = False
    for rrp in l:
        res = subn(rrp[0], Get(rrp[1]), text)
        if res[1]:
            replaced = True
            text = res[0]
    if replaced:
        return CommandResult(texts=[text])

replyList=[
    (regex, regexRoom, regexSender, _1Regex),
    (regexReplace, regexReplaceRoom, regexReplaceSender, _1RegexReplace),
]
        
def _1HandleRegexReply(chatroom, sender, text, tup):
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
        

def HandleRegexReply(message, options='', text='', continuous=CommandContinuousCallType.notContinuous, activate='', deactivate=''):
    text=text.lower()
    if continuous:
        chatroom = message.chatroom
        sender = message.sender
        for tup in replyList:
            ret = _1HandleRegexReply(chatroom, sender, text, tup)
            if ret:
                return ret
        return CommandResult.Failed()
    else:
        if text == 'on' or text == 'activate':
            activate = completeArg
        elif text=='off' or text=='deactivate':
            deactivate = completeArg
        ret = []
        if not IsEmpty(activate):
            a = (Activate(message.chatroom, message.sender, activate, True))
            if a:
                ret.append(a)
        if not IsEmpty(deactivate):
            d = (Activate(message.chatroom, message.sender, deactivate, False))
            if d:
                ret.append(d)
        if IsEmpty(ret):
            raise Exception('Invalid parameters')
        return CommandResult(texts=ret)

def Init(client):
    pass

regexReplyCmd = ContinuousTextCommand(
    'regexreply',
    HandleRegexReply,
    desc='Replies if regex matches.',
    initFunction = Init
)