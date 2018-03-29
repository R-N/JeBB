from line2.models.command import Command, Parameter, ParameterType, CommandResult, CommandResultType
from random import randint
from line2.utils import IsEmpty

def Randint(message, options, text='', low=0, high=0):
    if low == 0 and low==high:
        arr = text.split(' ')
        if len(arr) != 2:
            message.ReplyText("Please specify low & high parameter")
            return
        low = int(arr[0])
        high = int(arr[1])

    a = min(low, high)
    b = max(low, high)

    r = randint(a, b)

    message.ReplyText(str(r))
        

randintCmd = Command(
    'randint',
    Randint,
    desc='Random int'
)
