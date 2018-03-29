from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Sort(message, options, text=''):
    if IsEmpty(text):
        message.ReplyText("Please provide text")
        return
    s1s = text.split('\n')
    ss = []
    for s1 in s1s:
        s2s = s1.split(' ')
        ss.extend(s2s)

    ss.sort()
    return CommandResult(type=CommandResultType.done, texts=[' '.join(ss)])

sortCmd = Command(
    'sort',
    Sort,
    desc='Sort string'
)
