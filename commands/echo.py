from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Echo(message, options, text=''):
    if not IsEmpty(text):
        return CommandResult(type=CommandResultType.done, texts=[text])

echoCmd = Command(
    'echo',
    Echo,
    desc='Echoes'
)
