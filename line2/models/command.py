from re import compile, DOTALL
from line2.models.types import ParameterType, NoDefaultParameter, DefaultParameter, Type, CommandType, CommandResultType, CommandContinuousCallType, ChatroomType
from line2.utils import IsEmpty, Alphanumeric, Lock, GetBraceInsides, EscapeNames, Acquire
from traceback import format_exc, print_stack
from line2.models.events import ImageMessage, TextMessage
from line2.models.content import Image

noDefaultParameter = NoDefaultParameter()
defaultParameter = DefaultParameter()

def ParseArg(type, x, trial=False, name='x'):
    if type == ParameterType.raw:
        return x
    if type == ParameterType.list:
        if not isinstance(x, list):
            raise Exception("Argument '" + name + "' should be of 'list' type. Instead, we got " + str(x))
        return x
    if isinstance(x, CommandCall):
        if trial:
            return x
        x = x.result
    if isinstance(x, CommandResult):
        if type == ParameterType.images:
            return x.images
        if type == ParameterType.texts:
            return x.texts
        if type == ParameterType.str:
            return '\n'.join(x.texts)
    elif type == ParameterType.images:
        if isinstance(x, ImageMessage):
            x = x.image
        if isinstance(x, Image):
            x = [x]
        if not isinstance(x, list):
            raise Exception("Parameter '" + name + "' with 'images' type expects a list of ImageMessage, or list of Image")
        x2 = []
        for dx in x:
            if isinstance(x, ImageMessage):
                x2.append(x.image)
            elif isinstance(x, Image):
                x2.append(x)
            else:
                raise Exception("Parameter '" + name + "' with 'images' type expects a list of ImageMessage, or list of Image")
        x=x2
        return x
    elif isinstance(x, TextMessage):
        x = x.text
    elif isinstance(x, ImageMessage):
        pass
    if type == ParameterType.int:
        try:
            return int(x)
        except Exception:
            raise Exception("[Parameter.Parse] Argument '" + name + "' should be an integer. Instead we got '" + str(x) + "'")
    if type == ParameterType.float:
        try:
            return float(x)
        except Exception:
            raise Exception("[Parameter.Parse] Argument '" + name + "' should be a float (real number). Instead we got '" + str(x) + "'")
    if type == ParameterType.bool:
        try:
            return bool(x)
        except Exception:
            raise Exception("[Parameter.Parse] Argument '" + name + "' should be a boolean. Instead we got '" + str(x) + "'")
    if type == ParameterType.str:
        if isinstance(x, list):
            return '\n'.join([str(y) for y in x])
        return str(x)
    return x

class Parameter(object):
    def __init__(self, name, type = ParameterType.str, default = noDefaultParameter):
        self.type = type
        self.name = name
        self.default = default
        
        
    def Parse(self, x = defaultParameter, trial=False):
        if x == defaultParameter:
            if self.default == noDefaultParameter:
                raise Exception("[Parameter.Parse] Didnt pass parameter and no default parameter either")
            return self.default
        return ParseArg(self.type, x, trial, self.name)
    

class Command(object):
    defaultArgNames = {'message':0, 'options':0, 'text':0, 'admin':0, 'images':0}
    def __init__(self, name, function, params = None, desc = 'No description', initFunction=None, paramCheckFunction = None, escapeNames=True):
        self.escapeNames = escapeNames
        self.type = Type.command
        self.commandType = CommandType.text
        name = name.strip()
        name0 = Alphanumeric(name).lower().strip()
        if ' ' in name:
            raise Exception("[Command(" + name + "):__init__:1] Name must not contain spaces")
        if name0 == 'admin':
            raise Exception("[Command(" + name + "):__init__:2] Command cannot be named 'admin'")
        self.name = name
        self.function = function
        self.paramCheckFunction = paramCheckFunction
        self.images=[]
        self.imageCount = 0
        funcCode = function.__code__
        argCount = funcCode.co_argcount
        if argCount == 0:
            raise Exception("[Command(" + name + "):__init__:3] Function need to at least have one parameters named 'message'")
        args = funcCode.co_varnames
        if 'message' not in args:
            raise Exception("[Command(" + name + "):__init__:4] Function need to have parameter named 'message'")
        if IsEmpty(desc):
            self.desc = 'No description'
        else:
            self.desc = desc
        defaultArgs = function.__defaults__
        if defaultArgs is None:
            defaultArgs = []
            defaultArgCount = 0
        else:
            defaultArgCount = len(defaultArgs)
        x = (argCount-defaultArgCount)
        neededArgs = args[:x]
        optionalArgs = args[x:]
        self.neededArgs = {}
        self.optionalArgs = {}
        self.args = {}
        self.allArgs = {}
        if params is not None:
            for param in params:
                self.allArgs[param.name] = 0
                if param.name == 'message':
                    continue
                if param.name not in args:
                    raise Exception("[Command(" + name + "):__init__:5] Param name not used in the function")
                if isinstance(param.default, NoDefaultParameter):
                    self.neededArgs[param.name] = param
                else:
                    self.optionalArgs[param.name] = param
                self.args[param.name] = param
        self.optionalArgs = {}
        for x in neededArgs:
            self.allArgs[x] = 0
            if x == 'message':
                continue
            if x not in self.args:
                if x == 'options':
                    p = Parameter('options', type=ParameterType.str, default = '')
                    self.optionalArgs[x] = p
                    self.args[x] = p
                    continue
                elif x == 'text':
                    p = Parameter('text', type=ParameterType.str, default = '')
                    self.optionalArgs[x] = p
                    self.args[x] = p
                    continue
                elif x == 'admin':
                    p = Parameter('admin', type=ParameterType.bool, default = True)
                    self.optionalArgs[x] = p
                    self.args[x] = p
                    continue
                else:
                    p = Parameter(x)
                self.neededArgs[x] = p
                self.args[x] = p
        for i in range(0, defaultArgCount):
            x = optionalArgs[i]
            self.allArgs[x] = 0
            if x == 'message':
                continue
            t = ParameterType.raw
            default = defaultArgs[i]
            if isinstance(default, int):
                t = ParameterType.int
            elif isinstance(default, float):
                t = ParameterType.float
            elif isinstance(default, bool):
                t = ParameterType.bool
            elif isinstance(default, str):
                t = ParameterType.str
            elif isinstance(default, list):
                if x == 'texts':
                    t = ParameterType.texts
                elif x == 'images':
                    t = ParameterType.images
                else:
                    t = ParameterType.list
            elif default is None:
                t = ParameterType.raw
            param = Parameter(x, type = t, default = default)
            if x in self.neededArgs:
                del self.neededArgs[x]
            self.optionalArgs[x] = param
            self.args[x] = param
        if initFunction is not None:
            if 'client' not in initFunction.__code__.co_varnames:
                raise Exception("[Command(" + name + "):__init__:6] initFunction must have 'client' as an argument and other arguments must be optional if any.")
        self.initFunction = initFunction
        self.customNeededArgs = {k:v for k, v in self.neededArgs.iteritems() if k not in self.defaultArgNames}
        self.customNeededArgCount = len(self.customNeededArgs)
        self.wantOptions = 'options' in self.args
        self.needOptions = 'options' in self.neededArgs
        
    
    def CheckArgs(self, args):
        if self.paramCheckFunction is None:
            return True
        try:
            if self.paramCheckFunction(**args) != False:
                return True
            raise Exception("Wrong parameters")
        except Exception as e:
            msg.ReplyText("[Command(" + self.name + ").CheckArgs:1] " + str(e))
        return False
    
    _1regex = compile('^ *([^=]+)= *')
    _1regex2 = compile('([^=]+)(=?)')
    
    def ParseArg(self, msg, text, stack=None, args = None):
        m1 = self._1regex.match(text)
        if m1 is None:
            return None
        l = text.split('=', 1)
        name = l[0]
        read = len(name)
        name = name.strip()
        rest = ""
        if len(l) > 1:
            read = read+1
            rest = text[read:]
        read2 = 0
        px = ""
        if not IsEmpty(rest):
            read2, px = self.ParseRest(msg, rest, stack, args)
        
        read=read+read2
        #print("PARSEARG READ2 %s PX %s" % (str(read2), str(px)))
        return (read, name, px)
    
    def ParseRest(self, msg, rest, stack=None, args=None):
        if IsEmpty(rest):
            return (0, '')
        px = None
        if rest[0] == '/':
            px, start, end = GetBraceInsides(rest[1:], '(/', "\\)", omitOuter=True)
            #print("PARSEREST / px=%s" % px)
        if rest[:2] == '(/':
            px, start, end = GetBraceInsides(rest, '(/', "\\)")
            #print("PARSEREST (/ px=%s" % px)
        if px is not None:
            read=end
            name, x, args = px.partition(' ')
            cmd = None
            if name in msg.client._1commands:
                cmd = msg.client._1commands[name]
            elif args and 'admin' in args and args['admin'] and name in msg.client._1adminCommands:
                cmd = msg.client._1adminCommands[name]
            if cmd is not None:
                cmdArgs = cmd.ParseArgs(msg, text=args, stack=stack)
                cmdCall = stack.Add(cmd, args=cmdArgs)
                #print("PARSEREST READ %d CMDCALL %s" % (read, str(cmdCall)))
                return (read, cmdCall)
        l = rest.split('=', 1)
        if len(l) == 1:
            return (len(rest), rest)
        px = l[0]
        if IsEmpty(px):
            return (0, "")
        a = px.rstrip().rsplit(' ', 1)
        if len(a) == 1:
            return (len(rest), rest)
        a1 = a[1]
        if (not IsEmpty(a1)) and a1 in self.args and (args is None or a1 not in args):
            px = a[0]
            read = len(px)
        else:
            px = px + '='
            read = len(px)
            #print("RECURSING PARSEREST " + rest[read:])
            b = self.ParseRest(msg, rest[read:], stack, args)
            read = read + b[0]
            px = px + b[1]
        return (read, px)
        
    
    _1desc = {'help':0, 'desc':0, 'description':0, 'usage':0, 'how':0, 'howto':0, 'how to':0, 'howtouse':0, 'how to use':0}
    _1optionRegex = compile('^ *-o *([^ ]+)? *')
    
    def ParseArgs(self, msg, text=None, stack = None, args=None):
        if args is None:
            args = {}
        text0=text
        options = ''
        for k in args.keys():
            if k not in self.allArgs:
                del args[k]
        if not IsEmpty(text):
            if self.wantOptions:
                #print("WANT OPTIONS")
                mOp = self._1optionRegex.match(text)
                if mOp is not None:
                    #print("MOP IS NOT NONE")
                    options = mOp.group(1)
                    text = text[mOp.span()[1]:]
            #if self.customNeededArgCount > 0:
            text0 = text
            while True:
                c = self.ParseArg(msg, text, stack, args)
                if c is None:
                    break
                text = text[c[0]:]
                name = c[1]
                if name in self.args and name not in args:
                    t = self.args[name].Parse(c[2], trial=True)
                    args[name] = c[2]
        if self.wantOptions and 'options' not in args:
            args['options'] = options
        args['message'] = msg             
        if 'text' in self.args and 'text' not in args:
            #print("SETTING TEXT")
            args['text'] = self.ParseRest(msg, text0, stack, args)[1]
        z = {x.name : ParameterType.toString[x.type]  for x in self.neededArgs.itervalues() if x.name not in args}
        if len(z) > 0:
            raise Exception("Needed Argument " + str(z) + " not provided\n" + self.desc)
        
        #print("PARSEARG ARGS " + str(args))
        return args
    
    def Desc(self, msg, text):
        t = text.strip().lower()
        if t in self._1desc:
            msg.ReplyText("[Command(" + self.name + ").description]\n" + self.desc)
            return CommandResult(type=CommandResultType.description, message=msg)
        return CommandResult(type=CommandResultType.failed, message=msg)
    
    
    def Call(self, msg, text=None, stack=None, args=None):
        if args is None:
            args = {}
        try:
            if not IsEmpty(text):
                args.update(self.ParseArgs(text))
            for k, v in args.items():
                if k in self.args and k not in self.defaultArgNames:
                    args[k] = self.args[k].Parse(v, trial=False)
                elif k in self.allArgs:
                    if k == 'text':
                        args[k] = ParseArg(ParameterType.str, v, trial=False, name='text')
                    else:
                        args[k] = v
                else:
                    del args[k]
            if 'params' in self.args:
                args['params'] = args
            if self.CheckArgs(args):
                ret = self.function(**args)
                if isinstance(ret, CommandResult):
                    if not ret.message or not ret.chatroom or not ret.sender:
                        ret.SetMessage(msg, escapeNames = self.escapeNames)
                    return ret
                return CommandResult(message=msg, escapeNames=self.escapeNames)
        except Exception as e:
            msg.client.Report(format_exc())
            msg.ReplyText("[Command(" + self.name + ").Call] " + str(e))
        return CommandResult(type=CommandResultType.failed, message=msg, escapeNames=self.escapeNames)

    
    
class ImageCommand(Command):
    def __init__(self, name, function, params = None, desc = 'No description', initFunction = None, images=["the image"], paramCheckFunction = None, escapeNames=True):
        Command.__init__(self, name, function, params, desc, initFunction, paramCheckFunction, escapeNames)
        if images is None or (not isinstance(images, str) and not (isinstance(images, list) and len(images) > 0)):
            raise Exception("[ImageCommand(" + name + ").__init__:1] 'images' must be a list of string and it can't be empty")
        if isinstance(images, str):
            images = [images]
        self.commandType = CommandType.image
        if 'images' not in self.args:
            raise Exception("[ImageCommand(" + name + ").__init__:2] 'function' needs to have 'images' parameter")
        self.images = images
        self.imageCount = len(images)
        Command.imageCount = self.imageCount
        
        
class HybridCommand(ImageCommand):
    def __init__(self, name, function, params = None, desc = 'No description', initFunction = None, images=["the image"], paramCheckFunction = None, escapeNames=True):
        ImageCommand.__init__(self, name, function, params, desc, initFunction, images, paramCheckFunction, escapeNames)
        self.commandType = CommandType.hybrid
        if self.args['images'].default == noDefaultParameter:
            raise Exception ("[HybridCommand(" + name + ").__init__:1] Parameter 'images' must have a default value")
        
class ContinuousTextCommand(Command):
    def __init__(self, name, function, params = None, desc = 'No description', initFunction=None, paramCheckFunction = None, escapeNames=True):
        Command.__init__(self, name, function, params, desc, initFunction, paramCheckFunction, escapeNames)
        if 'text' not in self.args:
            raise Exception("[ContinuousTextCommand(" + name + ").__init__:2] 'function' needs to have 'text' parameter")
        

class ContinuousImageCommand(ImageCommand):
    def __init__(self, name, function, params = None, desc = 'No description', initFunction = None, images=["the image"], paramCheckFunction = None, escapeNames=True):
        ImageCommand.__init__(self, name, function, params, desc, initFunction, images, paramCheckFunction, escapeNames)

class ContinuousHybridCommand(HybridCommand):
    def __init__(self, name, function, params = None, desc = 'No description', initFunction = None, images=["the image"], paramCheckFunction = None, escapeNames=True):
        HybridCommand.__init__(self, name, function, params, desc, initFunction, images, paramCheckFunction, escapeNames)
        if 'text' not in self.args:
            raise Exception("[ContinuousTextCommand(" + name + ").__init__:2] 'function' needs to have 'text' parameter")
        if self.args['text'].default == noDefaultParameter:
            raise Exception ("[HybridCommand(" + name + ").__init__:1] Parameter 'text' must have a default value")
            
    
class CommandResult(object):
    def __init__(self, type = CommandResultType.done, texts=None, images=None, value=None, message=None, chatroom=None, sender=None, escapeNames=True, askImage=None):
        self.escapeNames = escapeNames
        if message:
            chatroom = message.chatroom
            if message.sender:
                sender = message.sender
        if not sender and chatroom and chatroom.chatroomType == ChatroomType.user:
            sender = chatroom
        self.type = type
        self.message = message
        self.chatroom = chatroom
        self.sender = sender
        if texts is None:
            if isinstance(value, str):
                self._texts = [EscapeNames(chatroom, sender, value)]
            elif isinstance(value, list) and len([x for x in value if not isinstance(x, str)]) == 0:
                self._texts = [EscapeNames(chatroom, sender, v) for v in value]
            else:
                self._texts = None
        else:
            if isinstance(texts, str):
                self._texts = [ExcapeNames(chatroom, sender, texts)]
            else:
                self._texts = [EscapeNames(chatroom, sender, t) for t in texts]
        if isinstance(images, ImageMessage):
            images = images.image
        if isinstance(images, Image):
            images = [images]
        self.images = images
        self.value = value
        self.askImage = askImage
        
    @staticmethod
    def Done(*args, **kwargs):
        return CommandResult(type=CommandResultType.done, *args, **kwargs)
        
    @staticmethod
    def Failed(*args, **kwargs):
        return CommandResult(type=CommandResultType.failed, *args, **kwargs)
        
    @staticmethod
    def ExpectImage(*args, **kwargs):
        return CommandResult(type=CommandResultType.expectImage, *args, **kwargs)
        
    @staticmethod
    def Description(*args, **kwargs):
        return CommandResult(type=CommandResultType.description, *args, **kwargs)
        
    @property
    def texts(self):
        return self._texts
    
    @texts.setter
    def texts(self, value):
        if isinstance(value, str):
            value = [value]
        elif value and not isinstance(value, list):
            raise Exception("[CommandResult] 'texts' expects a list of strings")
        self._texts = value
        if self.escapeNames:
            self.EscapeNames()
        
    def EscapeNames(self):
        self._texts = [EscapeNames(self.chatroom, self.sender, t) for t in self.texts]
        
    def SetChatroom(self, chatroom):
        if chatroom and self.chatroom != chatroom:
            self.chatroom = chatroom
            return True
        return False
    
    def SetSender(self, sender):
        if sender and self.sender != sender:
            self.sender = sender
            return True
        return False
        
    def SetMessage(self, msg, escapeNames=None):
        self.message = msg
        changed = self.SetChatroom(msg.chatroom) or self.SetSender(msg.sender)
        if changed:
            if escapeNames is None:
                escapeNames = self.escapeNames
            if escapeNames and not IsEmpty(self.texts):
                self.EscapeNames()
            return True
        return 
    
class CommandCall(object):
    def __init__(self, cmd, msg, text=None, stack=None, args=None, images=None):
        if args is None:
            args = {}
        if images is None:
            images = []
        self.lock = Lock()
        with Acquire(self.lock):
            self.cmd = cmd
            self.msg = msg
            self.stack = stack
            if not IsEmpty(text):
                args.update(cmd.ParseArgs(msg, text, stack, args))
            self._1args = args
            self.wantedImageCount = cmd.imageCount
            self.images = (images + args.get('images', []))[:self.wantedImageCount]
        
    def CallImage(self, msg):
        try:
            bytes = msg.bytes
        except Exception as e:
            msg.ReplyText("[Command(" + self.cmd.name + ").Image] Failed to download image\n" + str(e))
            return CommandResult(type=CommandResultType.failed, message=msg, escapeNames=self.cmd.escapeNames)
            
        self.AddImage(msg)
        if self.cmd.commandType == CommandType.image and not self.full:
            self.AskImage()
            return CommandResult.ExpectImage(message=msg, escapeNames=self.cmd.escapeNames)
        return self.Call()
        
    @property
    def full(self):
        return len(self.images) >= self.wantedImageCount
    
    @property
    def imageCount(self):
        return len(self.images)
    
    @property
    def index(self):
        return len(self.images)
    
    @property
    def args(self):
        images = None
        if self.wantedImageCount > 0:
            if len(self.images) > 0:
                images = self.images[:self.wantedImageCount]
        if images is None:
            if 'images' in self.cmd.neededArgs:
                self._1args['images'] = []
            elif 'images' in self._1args:
                del self._1args['images']
            
        else:
            self._1args['images'] = images
        return self._1args
    
    def Set(self, name, value):
        if name == 'images':
            self.images = value + self.images
        else:
            self._1args[name] = value
            
    def AddImage(self, image):
        with Acquire(self.lock):
            self.images.append(image)
        
    def AskImage(self, s = None):
        if self.full:
            return
        index = self.index
        if not s:
            s = self.cmd.images[index]
        self.msg.chatroom.SendText("[Command(" + self.cmd.name + ").Image:" + str(index) + "] Plase send " + s)
    
    def Update(self, args):
        images = self._1args.pop('images', None)
        if images:
            self.images = images + self.images
        self._1args.update(args)
        
    def Call(self, msg=None):
        if self.msg is None:
            self.msg = msg
        else:
            msg = self.msg
        if self.cmd.commandType == CommandType.image:
            if not self.full:
                self.AskImage()
                return CommandResult.ExpectImage()
        ret = self.cmd.Call(msg, stack=self.stack, args=self.args)
        self.result = ret
        if ret.type == CommandResultType.expectImage:
            self.AskImage(ret.askImage)
        #print("CALLED COMMAND %s %s" % (self.cmd.name, str(self)))
        return ret
        
class CommandStack(object):
    def __init__(self, msg, baseArgs=None):
        if baseArgs is None:
            baseArgs = {}
        self.lock = Lock()
        with Acquire(self.lock):
            self.msg = msg
            self.baseArgs = baseArgs
            self.stack = []
        
    def Add(self, cmd, msg=None, text=None, args=None, images=None):
        if args is None:
            args = {}
        if images is None:
            images = []
        if msg is None:
            msg = self.msg
        args0 = dict(self.baseArgs)
        args0.update(args)
        args = args0
        cmdCall = CommandCall(cmd=cmd, msg=msg, text=text, stack=self, args=args,images=images)
        with Acquire(self.lock):
            #print("ADDING %s TO COMMAND STACK %s" % (cmdCall.cmd.name, str(self)))
            self.stack.append(cmdCall)
        return cmdCall
            
    def Call(self, msg=None, ret=None):
        #print("ENTERING COMMANDSTACK " + str(self) + " CALL LOOP MSG=" + str(msg))
        with Acquire(self.lock):
            while True:
                if len(self.stack) == 0:
                    #print("COMMANDSTACK " + str(self) + "  IS EMPTY")
                    break
                if msg is None:
                    msg = self.msg
                cmdCall = self.stack[0]
                #print("CALLING COMMANDCALL " + str(self) + "  %s, STACK %s" % (cmdCall.cmd.name, [x.cmd.name for x in self.stack]))
                ret = cmdCall.Call(msg)
                if not ret:
                    ret = CommandResult(type=CommandResultType.done, message=msg)
                #print("CALLED COMMANDCALL " + str(self) + " ")
                msg = None
                if ret.type == CommandResultType.done:
                    #print("REMOVING COMMANDCALL " + str(self) + "  DONE, RESULT TEXTS=%s" % str(ret.texts))
                    self.stack.remove(cmdCall)
                else:
                    break
            #print("EXITED COMMANDSTACK " + str(self) + "  CALL LOOP")
            if not ret:
                ret = CommandResult(type=CommandResultType.done, message=msg)
            return ret
            
        
    def CallImage(self, msg, ret = None):
        with Acquire(self.lock):
            cmdCall = self.stack[0]
            ret = cmdCall.CallImage(msg)
            if ret.type == CommandResultType.done:
                self.stack.remove(cmdCall)
                return self.Call(msg=msg, ret=ret)
            if not ret:
                ret = CommandResult(type=CommandResultType.done, message=msg)
            return ret
    
    
    
    