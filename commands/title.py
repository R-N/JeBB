from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Title(message, options, text=''):
    if not IsEmpty(text):
        return CommandResult(type=CommandResultType.done, texts=[text.title()])

titleCmd = Command(
    'title',
    Title,
    desc='Makes Your Message Look Like This'
)
