from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Sort(message, options, text=''):
    if IsEmpty(text):
        message.ReplyText("Please provide text")
        return

    s1s = text.split('\n')
    s1s2 = []
    for s1 in s1s:
        s2s = s1.split('.')
        s2s2 = []
        for s2 in s2s:
            s3s = s2.split(';')
            s3s2 = []
            for s3 in s3s:
                s4s = s3.split(',')
                s4s2 = []
                for s4 in s4s:
                    s5s2 = s4.split(' ')
                    try:
                        s5s2 = [int(x) for x in s5s2]
                        s5s2.sort()
                        s5s2 = [str(x) for x in s5s2]
                    except Exception:
                        s5s2.sort()
                    s4s2.append(' '.join(s5s2))
                s3s2.append(','.join(s4s2))
            s2s2.append(';'.join(s3s2))
        s1s2.append('.'.join(s2s2))
    text = '\n'.join(s1s2)
                
    return CommandResult(type=CommandResultType.done, texts=[text])

sort2Cmd = Command(
    'sort2',
    Sort,
    desc='Sort string (2)'
)
