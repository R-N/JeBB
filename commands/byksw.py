from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Byksw(message, options, text=''):
    if IsEmpty(text):
        message.ReplyText("Please specify 'text' argument.")
        return
    
    vocal_w = 'AaEeOoUu'
    vocal_y = 'Ii'
    ret = ""

    for c in text:
        if c in vocal_w:
            if c.isupper():
                ret += 'W'
            else:
                ret += 'w'
        elif c in vocal_y:
            if c.isupper():
                ret += 'Y'
            else:
                ret += 'y'
        else:
            ret += c
    
    return CommandResult(type=CommandResultType.done, texts=[ret])


bykswCmd = Command(
    'byksw',
    Byksw,
    desc='Swmwgw byksw mwmbwry kwrtw'
)
