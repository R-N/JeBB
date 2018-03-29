from line2.models.command import ContinuousTextCommand, Parameter, ParameterType, CommandResultType, CommandResult, CommandContinuousCallType
from line2.utils import IsEmpty, Lock, AddAtExit, DelAtExit
from line2.models.messages import Buttons
from random import randint
from re import compile, DOTALL
from itertools import permutations
from time import time
    
    

solveRx = compile(" *(\d+) *(\d+) *(\d+) *(\d+)")
operators = ['+', '-', '*', '/', '%']

def FloatToStr(f):
    return "%g" % f

def Eval(text):
    ret = float(eval(text))
    return ret == 24

brackets = [
    ("%g%s%g%s%g%s%g", "%lf%s%lf%s%lf%s%lf"),
    ("(%g%s%g)%s%g%s%g", "(%lf%s%lf)%s%lf%s%lf"),
    ("%g%s%g%s(%g%s%g)", "%lf%s%lf%s%(lf%s%lf)"),
    ("%g%s(%g%s%g)%s%g", "%lf%s(%lf%s%lf)%s%lf"),
    ("(%g%s%g)%s(%g%s%g)", "(%lf%s%lf)%s(%lf%s%lf)"),
    ("(%g%s%g%s%g)%s%g", "(%lf%s%lf%s%lf)%s%lf"),
    ("((%g%s%g)%s%g)%s%g", "((%lf%s%lf)%s%lf)%s%lf"),
    ("(%g%s(%g%s%g))%s%g", "(%lf%s(%lf%s%lf))%s%lf"),
    ("%g%s(%g%s%g%s%g)", "%lf%s(%lf%s%lf%s%lf)"),
    ("%g%s((%g%s%g)%s%g)", "%lf%s((%lf%s%lf)%s%lf)"),
    ("%g%s(%g%s(%g%s%g))", "%lf%s(%lf%s(%lf%s%lf))")
]

def TryBrackets(msg24):
    ret = ''
    ops = [operators[int(msg24[1])], operators[int(msg24[3])], operators[int(msg24[5])]]
    for b in brackets:
        try:
            s = b[1] % (msg24[0], ops[0], msg24[2], ops[1], msg24[4], ops[2], msg24[6])
            if Eval(s):
                ret = b[0] % (msg24[0], ops[0], msg24[2], ops[1], msg24[4], ops[2], msg24[6])
                break
        except Exception:
            pass
    
        
    return ret

def TryOperators(msg24, i):
    if i==3:
        return TryBrackets(msg24)
    else:
        for j in range(0, 4):
            msg24a = [msg24[0], msg24[1], msg24[2], msg24[3], msg24[4], msg24[5], msg24[6]]
            msg24a[1 + 2*i] = j
            s = TryOperators(msg24a, i+1)
            if s:
                return s
    return ''


def Solve(text):
    mSolveRx = solveRx.match(text)
    if not mSolveRx:
        return ''
    nums = [mSolveRx.group(1), mSolveRx.group(2), mSolveRx.group(3), mSolveRx.group(4)]
    print("nums=%s" % nums)
    for i in range(0, 4):
        x = nums[i]
        if IsEmpty(x):
            return "Need 4 numbers separated by a space"
        y = None
        try:
            y = float(x)
        except Exception:
            return "Invalid number '" + str(x) + "'"
        nums[i] = y
    for x in permutations(nums):
        msg24a = [x[0], -1, x[1], -1, x[2], -1, x[3]]
        s = TryOperators(msg24a, 0)
        if s:
            return s
    return ''
            
def IsValid(text):
    if not IsEmpty(text):
        c = text[0] 
        return c == '(' or c.isdigit()
    return False
    

class Room(object):
    exRx = compile("(\()* *(\d+) *(\(|\))* *(\+|\-|\*|\/|\%) *(\(|\))* *(\d+) *(\(|\))* *(\+|\-|\*|\/|\%) *(\(|\))* *(\d+) *(\(|\))* *(\+|\-|\*|\/|\%) *(\(|\))* *(\d+) *(\))*")
    def __init__(self, obj, top=None, bot=None, addAtExit=True):
        self.obj = obj
        self.nums = None
        self.lock = Lock()
        self.top = 13
        self.bot = 1
        self.lastGenerated = 0
        if addAtExit:
            AddAtExit(self, self.__del__)
        self.Set(top, bot)
        
    def __del__(self):
        with self.lock:
            if self.nums:
                self.SendText("Shutting down")
                self.Stop(True)
                DelAtExit(self)
        
    def Set(self, top=None, bot=None):
        with self.lock:
            prevTop = self.top
            prevBot = self.bot
            if top is not None:
                if top == 0:
                    raise Exception("Can't be zero")
                self.top = top
            if bot is not None:
                if bot == 0:
                    raise Exception("Can't be zero")
                self.bot = bot
            if self.bot >= self.top:
                self.bot = prevBot
                self.top = prevTop
                raise Exception("Top cant be lower than or same as bot")
            if int(self.bot) != self.bot or int(self.top) != self.top:
                self.bot = prevBot
                self.top = prevTop
                raise Exception("Only integers are allowed")
            self.top = int(self.top)
            self.bot = int(self.bot)
            
        
    def Stop(self, force=False):
        if not force:
            t = self.CheckTime()
            if t:
                self.SendText("You have to wait %d seconds" % t)
                return CommandResult.Failed()
        with self.lock:
            if self.nums:
                s = " ".join(FloatToStr(x) for x in self.nums)
                s2 = Solve(s)
                self.SendText(s2)
            self.nums = None
            return CommandResult.Done()
        
    def Solve(self, text):
        with self.lock:
            if self.nums:
                self.SendText("Game is still running. Please stop it first if you want to solve. If the four numbers were also from me, just type '/24 next' to change the numbers and also give the answer")
                return CommandResult.Failed()
        s = Solve(text)
        if s:
            self.SendText(s)
        return CommandResult.Done()
    
    def Next(self, top=None, bot=None):
        with self.lock:
            ret = self.Stop()
            if ret.type == CommandResultType.failed:
                return ret
            self.Set(top, bot)
            return self.Generate()
        
    def CheckTime(self):
            delay = time() - self.lastGenerated
            if delay < 15:
                return round(15.5-delay)
            return 0
        
        
    def Generate(self, top=None, bot=None):
        with self.lock:
            self.Set(top, bot)
            top = self.top
            bot = self.bot
            while True:
                nums = [randint(bot, top), randint(bot, top), randint(bot, top), randint(bot, top)]
                print("GENERATE %s" % nums)
                s = " ".join(FloatToStr(x) for x in nums)
                s2 = Solve(s)
                if IsValid(s2):
                    print("VALID NUM s2=%s" % s2)
                    nums.sort()
                    self.nums = nums
                    break
                print("INVALID NUM s=%s" % s) 
            self.lastGenerated = time()
            return self.Send()
        
    def SendText(self, text):
        return self.obj.SendText("[TwentyFour]\n%s" % text)
        
    def SendButtons(self, buttons):
        if not buttons.columnText.startswith("[TwentyFour]"):
            buttons.SetColumnText("[TwentyFour]\n%s" % buttons.columnText)
            buttons.SetAltTextHeader("[TwentyFour]\n%s" % buttons.altTextHeader)
        return self.obj.SendButtons(buttons)
        
    def Send(self):
        if self.nums:
            buts = Buttons(" ".join(FloatToStr(x) for x in self.nums))
            buts.AddButton(
                "Next",
                "/24 next",
                "\nTo give up and ask for next numbers, type '/24 next'"
            )
            buts.AddButton(
                "Stop",
                "/24 stop",
                "\nTo just give up, type '/24 stop'"
            )
        else:
            buts = Buttons("Game is not running")
            buts.AddButton(
                "Create",
                "/24 create",
                "\nTo run it, type '/24 create'"
            )
        self.SendButtons(buts)
        return CommandResult.Done()
    
    
    def Eval(self, text, sender=None):
        with self.lock:
            if not self.nums:
                return CommandResult.Failed()
            text = text.strip()
            if not IsValid(text):
                return CommandResult.Failed()
            mExRx = Room.exRx.match(text)
            if not mExRx:
                return CommandResult.Failed()
            nums = None
            try:
                nums = [float(mExRx.group(2)), float(mExRx.group(6)), float(mExRx.group(10)), float(mExRx.group(14))]
            except Exception as e:
                self.SendText("Error. Invalid numbers.\n%s" % (s, e))
                return CommandResult.Done()
            try:
                for i in range(0, 4):
                    x = nums[i]
                    if x < self.bot or x > self.top:
                        raise Exception("Only integers ranging from %d-%d are allowed. %g is not in range" % (self.bot, self.top, x))
                    y = int(x)
                    if x != y:
                        raise Exception("Only integers ranging from %d-%d are allowed. %g is not an integer" % (self.bot, self.top, x))
                    nums[i] = y
            except Exception as e:
                self.SendText("Error. Invalid numbers.\n%s" % (s, e))
                return CommandResult.Done()
            nums.sort()
            if nums != self.nums:
                self.SendText("Error. Invalid numbers.\n%s != %s" % (nums, self.nums))
                return CommandResult.Done()
            s = ''
            for i in range(1, 16):
                c = mExRx.group(i)
                if c:
                    s = s+c
            try:
                name = ''
                if sender and sender.name:
                    name = ", %s" % sender.name
                ret = float(eval(text))
                if ret == 24:
                    rep = "Correct%s.\n%s == 24"
                    self.SendText(rep % (name, s))
                    return self.Generate()
                else:
                    rep = "Wrong%s.\n%s == %g"
                    self.SendText(rep % (name, s, ret))
            except Exception as e:
                self.SendText("Error. '%s' may not be a valid math expression.\n%s" % (s, e))
            return CommandResult.Done()


rooms = {}
lock = Lock()

def TwentyFour(message, options='', text='', continuous = CommandContinuousCallType.notContinuous, action = '', solve='', top=None, bot=None):
    if continuous:
        if message.chatroom not in rooms:
            return CommandResult.Failed()
        return rooms[message.chatroom].Eval(text, message.sender)
    else:
        if IsEmpty(action):
            action = text
        if action == 'create' or (IsEmpty(action) and IsEmpty(solve)):
            with lock:
                if message.chatroom in rooms:
                    room = rooms[message.chatroom]
                    if not room.nums:
                        return room.Generate()
                    return room.Send()
                else:
                    room = Room(message.chatroom, top, bot)
                    rooms[message.chatroom] = room
                    return room.Generate()
        else:
            with lock:
                if message.chatroom in rooms:
                    room = rooms[message.chatroom]
                else:
                    room = Room(message.chatroom, top, bot)
                    rooms[message.chatroom] = room
            if solve:
                return room.Solve(solve)
            elif action == 'next':
                return room.Next(top, bot)
            elif action == 'stop':
                return room.Stop()
            else:
                return room.Send()
            
            
            
                

twentyFourCmd = ContinuousTextCommand(
    "twentyfour",
    TwentyFour,
    desc="Use the 4 given numbers to form a math expression equal to 24. You can only use *+-/% operators. All of the number combinations are guaranteed to have solution. Hint : % is very useful."
)