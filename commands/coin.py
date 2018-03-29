from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Coin(message, options, text=''):
    if random() > 0.5:
        message.ReplyText("Heads")
    else:
        message.ReplyText("Tails")

coinCmd = Command(
    'coin',
    Coin,
    desc='Coin flip'
)
