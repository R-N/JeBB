from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty

def CommandList(message, options, text='', admin=False):
    client = message.client
    if admin:
        if client.hasAdminCommands:
            l = sorted([x for x in client._1adminCommands.items()])
            s = 'Admin commands :'
            for k, v in l:
                si = "\n%s" % k
                if k != v.name:
                    si = si + (" (%s)" % v.name)
                s = s + si
            return CommandResult.Done(texts=[s])
        return CommandResult.Done(texts=['No admin command registered'])
    elif client.hasCommands:
        l = sorted([x for x in client._1commands.items()])
        s = 'Commands :'
        for k, v in l:
            si = "\n%s" % k
            if k != v.name:
                si = si + (" (%s)" % v.name)
            s = s + si
        return CommandResult.Done(texts=[s])
    return CommandResult.Done(texts=['No command registered'])

commandListCmd = Command(
    'commandlist',
    CommandList,
    desc='Command list'
)
