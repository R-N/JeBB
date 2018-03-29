

from sys import _current_frames, version_info

py3 = version_info[0] > 2
py2 = version_info[0] < 3

PY3 = py3
PY2 = py2


def UTF8():
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")

if py2:
    UTF8()

def DisableHTTPSVerif():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    import ssl
    try:
        _create_unverified_https_context = ssl._1create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._1create_default_https_context = _create_unverified_https_context

DisableHTTPSVerif()

from re import compile
from threading import RLock, Condition, currentThread
import threading
from traceback import format_stack, print_exc
from time import time
from contextlib import contextmanager

from threading import currentThread
from time import sleep
from os import _exit, kill, getpid
from signal import signal, SIGTERM, SIG_DFL


def Clean(s):
    return s.decode('utf-8', 'ignore').encode('utf-8')
    
def Clean2(s):
    b = bytes(text, 'utf-8', 'ignore')
    s2 = decode(b, 'utf-8', 'ignore')
    b2 = encode(s2, 'utf-8', 'ignore')
    return str(b2, 'utf-8', 'ignore')

if version_info[0] > 2:
    Clean = Clean2

def _print(s):
    print(s)

if version_info[0] > 2:
    #_print = print
    pass


printLock = RLock()
def Print(*args, **kwargs):
    with printLock:
        _print(*args, **kwargs)

if version_info[0] > 2:
    #print = Print
    pass

def Frame2String(frame):
    # from module traceback
    lineno = frame.f_lineno # or f_lasti
    co = frame.f_code
    filename = co.co_filename
    name = co.co_name
    s = '  File "{}", line {}, in {}'.format(filename, lineno, name)
    line = linecache.getline(filename, lineno, frame.f_globals).lstrip()
    return s + '\n\t' + line

def Thread2List(frame):
    l = []
    while frame:
        l.insert(0, frame2string(frame))
        frame = frame.f_back
    return l

def FormatThreadStack(thread):
    if not thread:
        return ''
    ident =  thread.ident
    if not ident:
        return ''
    frame = _current_frames()[thread.ident]
    l = Thread2List(frame)
    return '\n'.join(l)

class Lock(object):
    _id = 0
    _lock = RLock()
    def __init__(self, TLock = RLock):
        self.TLock = TLock
        with Lock._lock:
            self.id = Lock._id
            Lock._id+=1
        self.cond = None
        
        self.locks = 0
        self.lock = self.TLock()
        
        self._waitingList = []
        self._lock = RLock()
        self.stackTraces = []
        self.e = None
        
    def __del__(self):
        if Lock:
            o = Lock
        else:
            o = self
        if self.id+1 == o._id:
            with o._lock:
                if self.id+1 == o._id:
                    o._id-=1

    def Check(self):
        if self.lock.acquire(False):
            self.lock.release()
            return self
        return None
    
    def TryAcquire(self):
        if self.lock.acquire(False):
            return self
        return None
        
    def Acquire(self, timeout = 2):
        #print("Locks : " + str(self.locks) + ". Trying to acquire lock")# at\n" + ''.join(traceback.format_stack()))
        with self._lock:
            if self.cond is None:
                if self.lock.acquire(False):
                    return self._GotLock()
                elif self.locks == 0:
                    print("LOCKS SHOULDVE BEEN UNLOCKED BUT CANT BE ACQUIRED. RECREATING LOCK")
                    self.lock = self.TLock()
                    if not self.lock.acquire(False):
                        raise Exception("What the fuck")
                    return self._GotLock()
            if timeout <= 0 and self.cond is None and self.lock.acquire():
                return self._GotLock()
            cond = Condition(RLock())
            start = now = time()
            end = now + timeout
            tup = (cond, currentThread().name, start)
            with cond:
                with self._lock:
                    name = currentThread().name
                    #print("WAITING FOR CONDITION %s" % name)
                    self._waitingList.append(tup)
                while now < end:
                    if (self.cond == cond or self.cond is None) and self.lock.acquire(False):
                        with self._lock:
                            self.cond = None
                            #print("GOT LOCK %s %g" % (name, (now-start)))
                            return self._GotLock(tup)
                    else:
                        if tup not in self._waitingList:
                            if now < end:
                                with self._lock:
                                    name = currentThread().name
                                    #print("WAITING AGAIN FOR CONDITION %s %d" % (name, self.locks))
                                    self._waitingList.append(tup)
                        
                    #cond.acquire()
                    self._lock.release()
                    waitTime = min(end-now, 1)
                    try:
                        cond.wait(waitTime)
                    except Exception:
                        cond.acquire()
                        cond.wait(waitTime)
                    self._lock.acquire()
                    now = time()

            with self._lock:
                if self.cond == cond or cond is None:
                    with self._lock:
                        self.cond = None
                        return self._GotLock(tup)
                elif tup in self._waitingList:
                    self._waitingList.remove(tup)
            if self.cond:
                selfcond = str(id(self.cond))
            else:
                selfcond = "None"
            if self.e:
                raise Exception()
            s0 = "%s %s %d Lock acquiring timeout (%gs) Locks remain : %d %s " % (currentThread().name, str(id(cond)), self.id, now-start, self.locks, selfcond)
            s = s0 + "at\n" + FormatStack() + '\n' 
            i = 0
            for trace in self.stackTraces:
                s = s + ("[STACKTRACE:%d]\n%s" % (i, trace))
                i+=1
            s = s + '\nCurrent execution:\n' + FormatThreadStack(self.owner)
            print(s)
            self.e = s0
            raise Exception(s0)
        
    def _GotLock(self, tup = None):
        #print("One lock acquired. Locks : " + str(self.locks)))
        with self._lock:
            self.locks += 1
            self.cond = None
            #if self.locks != self.lock._RLock__count:
            #    raise Exception("[ACQUIRE] LOCK COUNT DOESNT MATCH")
            self.stackTraces.append(currentThread().name + "\n" + FormatStack())
            self.owner = currentThread()
            if tup is not None:
                while tup in self._waitingList:
                    self._waitingList.remove(tup)
        return self
    
    def _Release(self):
        try:
            with self._lock:
                self.lock.release()
                self.locks-=1
                self.stackTraces.pop()
                #if self.locks == 0:
                #    while self.lock._RLock__count > 1:
                #        self.lock.release()
                #    self.owner = None
                #    if self.lock._RLock__count > 0:
                #        raise Exception("Something else is holding on to the lock")
                #if self.locks != self.lock._RLock__count:
                #    raise Exception("[RELEASE] LOCK COUNT DOESNT MATCH")
            return True
        except Exception:
            pass
        return False
    
    def Release(self):
        #print("Locks : " + str(self.locks) + ". Trying to release lock at")# \n" + ''.join(traceback.format_stack()))
        #print("GETTING LOCK FOR RELEASE " +  str(self.id))
        with self._lock:
            #print("GOT LOCK FOR RELEASE " +  str(self.id))
            if self.locks == 1:
                wllen = len(self._waitingList)
                if wllen > 0:
                    cond = None
                    for i in range(0, wllen):
                        cond = self._waitingList[0]
                        if cond is not None:
                            break
                    if cond is not None:
                        #print("NOTIFYING %s %s %d at %g" % (str(id(cond[0])), cond[1], self.id, time()-cond[2],))
                        cond = cond[0]
                        self.cond = cond
                        self._Release()
                        """try:
                            cond.notifyAll()
                            try:
                                while True:
                                    cond.release()
                            except Exception:
                                pass
                        except Exception:
                            cond.acquire()
                            cond.notifyAll()
                            try:
                                while True:
                                    cond.release()
                            except Exception:
                                pass"""
                        with cond:
                            cond.notifyAll()
                            #while cond._Condition__lock._RLock__count > 1:
                            #    cond.notifyAll()
                            #    cond.release()
                            #if cond._Condition__lock._RLock__count == 0:
                            #    cond.acquire()
                            #cond.notifyAll()
                        return
            self._Release()
            
    def acquire(self):
        return self.Acquire()
    
    def release(self):
        return self.release()
        
    def __enter__(self):
        return self.Acquire()
    
    def __exit__(self, type, value, tb):
        self.Release()
        if type:
            while self.locks > 0:
                self.Release()
        return not type
    
    
atExit = {}
atExitLock = Lock()
atExitCond = Condition()

def AtExit(sig, frame):
    t = time()
    with atExitLock:
        print("ATEXIT %d" % sig)
        for k, x in atExit.items():
            try:
                x[0](*(x[1]), **(x[2]))
            except Exception:
                print_exc()
            if k in atExit:
                del atExit[k]
        while time() - t < 25 and len(atExit) > 0:
            with atExitCond:
                atExitCond.wait(1)
        signal(SIGTERM, SIG_DFL)
        _exit(0)
        #kill(int(getpid()), SIGTERM)
        return sig

def AddAtExit(key, method, args=[], kwargs={}, *args2, **kwargs2):
    with atExitLock:
        args0 = list(args)
        args0.extend(args2)
        kwargs0 = dict(kwargs2)
        kwargs0.update(kwargs)
        atExit[key] = (method, args0, kwargs0)
    
def DelAtExit(key):
    with atExitLock:
        if key in atExit:
            del atExit[key]
            if len(atExit) == 0:
                with atExitCond:
                    atExitCond.notifyAll()
    
def InitAtExit():
    print("register signal SIGTERM " + str(signal(SIGTERM, AtExit)))
    #print("register signal SIGINT " + str(signal.signal(signal.SIGINT, Test)))
        

def CreateBody(s):
    return [bytes(s, 'utf-8')]

def CreateBody2(s):
    return s

if version_info[0] < 3:
    CreateBody = CreateBody2

allAcquired = {}
@contextmanager
def Acquire(timeout=2, *locks0):
    if isinstance(timeout, Lock):
        locks0 = (timeout,) + locks0
        timeout = 2
    o = object()
    threadLocal = threading.local()
    acquired = getattr(threadLocal, "acquired", [])
    threadLocal.acquired=acquired

    locks = sorted(locks0, key=lambda x: id(x), reverse=True)  
    newLocks = [x for x in locks if x not in acquired]
    allLocks = sorted(newLocks + acquired, key=lambda x: id(x), reverse=True)
    # Check to make sure we're not violating the order of locks already acquired  
    i0 = id(allLocks[-1])
    i = i0-1
    for d in allAcquired.values():
        i = max(i, max(lock.id for lock in d[0]))
    st = format_stack()[:-2]
    st = ["%d:%s" % (i, st[i]) for i in range(0, len(st))]
    si = currentThread().name + '\n' + ''.join(st) + '\nLock ids : ' + str([x.id for x in locks])
    if i >= i0:
        s = "Lock Order Violation (%d, %d)" % (i, i0)
        for d in allAcquired.values():
            if lambda a, b: bool(set(locks).isdisjoint(d[0])):
                s = s + "\nTRACE\n" + d[1]
        s = s + "\nCURRENTTRACE\n" + si
        raise Exception(s)

    acquired.extend(locks)
    allAcquired[o] = (locks, si)
    try:
        for lock in locks:
            lock.Acquire(timeout=timeout)
    except Exception:
        pass
            
    yield locks0
    for lock in reversed(locks):
        lock.Release()
    del allAcquired[o]
        
class Locks(object):
    def __init__(self, auto=True, *locks):
        self.auto = auto
        self.locks = locks0
        locks = sorted(locks0, key=lambda x: id(x))  
        self.sLocks = locks
        self.rLocks = reversed(locks)
        
    @contextmanager
    def Acquire(self):
        local = threading.local()
        acquired = getattr(local,"acquired",[])
        # Check to make sure we're not violating the order of locks already acquired   
        if acquired:
            if max(id(lock) for lock in acquired) >= id(locks[0]):
                raise Exception("Lock Order Violation")
        acquired.extend(locks)
        local.acquired = acquired
        for x in self.sLocks:
            x.Acquire()
        return self
    
    @contextmanager
    def Release(self):
        local = threading.local()
        acquired = getattr(local,"acquired",[])
        for x in self.rLocks:
            x.Release()
        del acquired[-len(locks):]
        local.acquired = acquired
        
    def __enter__(self):
        if self.auto:
            self.Acquire()
        return self
    
    def __exit__(self, a, b, c):
        if self.auto:
            self.Release()
        return not a

def FormatStack():
    st = format_stack()[:-1]
    st = ["%d:%s" % (i, st[i]) for i in range(0, len(st))]
    return ''.join(st)

def IsEmpty(s):
    if isinstance(s, list):
        return len(s) == 0
    return not (s and (not isinstance(s, str) or s.strip()))


def ReplaceStringAtPosition(s, replacement, index, lengthReplaced = 0):
    if lengthReplaced==0:
        return s[:index] + replacement + s[(index+len(replacement)):]
    return s[:index] + replacement + s[(index+lengthReplaced):]

def FindAll(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)
        
def EscapeNames(chatroom, sender, text):
    if '{cr}' in text:
        name = 'this room'
        if chatroom:
            _name = chatroom.name
            if _name:
                name = _name
            text = text.replace('{cr}', name)
    if '{s}' in text:
        name = you
        if sender:
            _name = sender.name
            if _name:
                name = _name
        text = text.replace('{s}', name)
    return text
        
def GetBraceInsides(s, opening, closing, omitOuter=False):
    openings = list(FindAll(s, opening))
    closings = list(FindAll(s, closing))
    closingLen = len(closings)
    if closingLen == 0:
        return (s, 0, len(s))
    openingLen = len(openings)
    if openingLen == 0 and not omitOuter:
        return ('', 0, 0)
    if omitOuter:
        x = closingLen
        try:
            end = closings[openingLen]+1
        except Exception:
            end = closings[openingLen-1]+1
            x = 0
        return (s[:end], 0, end+x)
    start = openings[0]
    x = closingLen-1
    for i in range(0, openingLen):
        if openings[i] >= closings[i]:
            x = i-1
            break
    end = closings[x]+2
    return (s[start+len(opening):end-len(closing)], start, end)

def ParseList(s):
    px, start, end = GetBraceInsides(s, '[/', '\\]')
    if end == 0:
        raise Exception("Invalid list string")
    return px.split('/,\\')

emailRegex = compile(r"[^@]+@[^@]+\.[^@]+")


        

global _reverseLock
_reverseLock = Lock()
global _reverseDicts
_reverseDicts = []
global _hasReverseDict
_hasReverseDict = False
global _ns
_ns = []

def AddReverseDict(rd, ns = [1]):
    global _reverseLock
    with _reverseLock:
        global _reverseDicts
        _reverseDicts.append(rd)
        global _ns
        if len(ns) > 0:
            _ns = _ns + ns
        _ns.sort(reverse=True)
        global _hasReverseDict
        _hasReverseDict = True

def Alphanumeric(s):
    global _reverseLock
    with _reverseLock:
        global _hasReverseDict
        if not _hasReverseDict:
            return s
        l = s
        global _reverseDicts
        #global _ns
        #for n in _ns:
        #    for rd in _reverseDicts:
        #        l = ''.join([rd.get(c, c) for c in SplitByN(l, n)])
        #for rd in _reverseDicts:
        #    l = ''.join([rd.get(c, c) for c in s])
        for rd in _reverseDicts:
            for k, v in rd.items():
                l = l.replace(k, v)
        ret = l#''.join(l)
        return ret
    
def SplitByN(s, n):
    if isinstance(s, list):
        return [''.join(s[i:i+n]) for i in range(0, len(s), n)]
    return [s[i:i+n] for i in range(0, len(s), n)]
