from line2.api.line_0_10_0.ttypes import *

class WhenOALeave:
    reinvite = 0
    doNothing = 1
    leaveToo = 2

class UserType:
    mid = 0
    phone = 1
    email = 2
    userId = 3
    proximity = 4
    group = 5
    user = 6
    qrCode = 7
    promotionBot = 8

class UserStatus:
    unspecified = 0
    friend = 1
    friendBlocked = 2
    recommend = 3
    recommendBlocked = 4
    deleted = 5
    deletedBlocked = 6


class UserRelation:
    oneWay = 0
    twoWay = 1
    notRegistered = 2



class ParameterType:
    str = 0
    int = 1
    float = 2
    number = 2
    images = 3
    raw=4
    list = 5
    texts = 6
    bool = 7
    
    toString = ["string", "integer", "float (real number)", "Images", "Raw", "List", "Texts", "Boolean"]
    
class DefaultParameter:
    pass

class NoDefaultParameter:
    pass

class CommandType:
    text = 0
    image = 1
    hybrid = 2


class Type:
    chatroom = 0
    event = 1
    profile = 2
    command = 3
    
class ChatroomType:
    user = 0
    room = 1
    group = 2
    
class EventType:
    message = 0
    invited = 1
    joined = 2
    left = 3
    unfollowed = 4
    followed = 5
    update = 6
    
    toString=["message", "invited", "joined", "left", "unfollowed", "update"]
class MessageType:
    text=0
    sticker=1
    location=2
    content=3
    contact=4
    
class Receiver:
    none = 0
    oA = 1
    user = 2
    
    toString=["None", "OA", "User"]
    
class CommandResultType(object):
    failed = None
    done = None
    description = None
    expectImage = None
    
CommandResultType.failed = CommandResultType()
CommandResultType.done = CommandResultType()
CommandResultType.description = CommandResultType()
CommandResultType.expectImage = CommandResultType()

class CommandContinuousCallType:
    notContinuous = 0
    text = 1
    image = 2
    
class Rule:
    And = 0
    Or = 1
    All = {0:0, 1:1}
    