from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def MockSB(message, options, text=''):
    if IsEmpty(text):
        message.ReplyText("Please specify 'text' argument.")
        return
    text = text.lower()
    tlen = len(text)
    l = list(text)
    consUp = 0
    consLow = 0
    for i in range(0, tlen):
        if consUp >= 2:
            low = l[i]
            if low.upper() != low:
                consUp=0
                consLow=1
        elif consLow >=2:
            low = l[i]
            up = low.upper()
            if up != low:
                consUp=1
                consLow=0
                l[i] = up

        elif random() > 0.5:
            low = l[i]
            up = low.upper()
            if up != low:
                consUp=consUp+1
                consLow=0
                l[i] = up
        else:
            consLow=consLow+1
            consUp=0

    ret = "".join(l)
    #message.ReplyText(ret)
    return CommandResult(type=CommandResultType.done, texts=[ret])

mockSBCmd = Command(
    'mocksb',
    MockSB,
    desc='mOCkInG sPOnGeBoB'
)
