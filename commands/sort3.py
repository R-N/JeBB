from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Sort(message, options, text=''):
    if IsEmpty(text):
        message.ReplyText("Please provide text")
        return
    s1s = text.split('\n')
    d = {}
    for s1 in s1s:
        s2s = s1.split(' ')
        for s2 in s2s:
            s2a = ''.join([c for c in s2 if c.isalpha()])
            if not IsEmpty(s2a):
                s2 = s2a
            if s2 in d:
                d[s2] += 1
            else:
                d[s2] = 1
    d2 = {}
    for k, v in d.items():
        if v in d2:
            d2[v].extend([k] * v)
        else:
            d2[v] = [k] * v
    d3 = {}
    ss = []
    for k, v in d2.items():
        d3[k] = sorted(v)
    for k, v in sorted(d3.items()):
        ss.extend(v)
    return CommandResult(type=CommandResultType.done, texts=[' '.join(ss)])

sort3Cmd = Command(
    'sort3',
    Sort,
    desc='Sort string (3)'
)
