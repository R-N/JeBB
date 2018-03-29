from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Space(message, options, text=''):
    #print("SPACE TEXT=%s" % text)
    if not IsEmpty(text):
        return CommandResult(type=CommandResultType.done, texts=[' '.join(list(text.strip()))])

spaceCmd = Command(
    'space',
    Space,
    desc='S p a c e'
)
