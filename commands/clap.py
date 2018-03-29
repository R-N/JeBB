# -*- coding: utf-8 -*-
from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def Clap(message, options, text=''):
    if not IsEmpty(text):
        ret = text.replace(' ',' 👏 ').replace('👏 👏', '👏').replace('👏  👏', '👏')
        return CommandResult(type=CommandResultType.done, texts=[ret])

clapCmd = Command(
    'clap',
    Clap,
    desc='Makes 👏 your 👏 message 👏 look 👏 like 👏 this'
)
