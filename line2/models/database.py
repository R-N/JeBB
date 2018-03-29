from psycopg2 import connect
from traceback import format_exc
from time import sleep
from line2.utils import Lock
from sys import version_info

if version_info[0] < 3:
    import urlparse
else:
    import urllib
    from urllib import parse
    from urllib.parse import urlparse

class Database(object):
    def __init__(self, client, url):
        self.lock = Lock()
        with self.lock, client.lock:
            self.client = client
        with self.lock:
            self.connPool = []
            self.connCount = 0
            if version_info[0] < 3:
                urlparse.uses_netloc.append("postgres")
                self.url = urlparse.urlparse(url)
            else:
                urllib.parse.uses_netloc.append("postgres")
                self.url = urlparse(url)
        
    def CreateConnection(self):
        with self.lock:
            return connect(
                database=self.url.path[1:],
                user=self.url.username,
                password=self.url.password,
                host=self.url.hostname,
                port=self.url.port
            )
    
        
    @property
    def cursor(self):
        return self.GetCursor()
    
    def GetCursor(self):
        with self.lock:
            l = len(self.connPool)
            if l > 0:
                for i in range(l-1, -1, -1):
                    if self.connPool[i] is None or self.connPool[i].closed:
                        del self.connPool[i]
                    else:
                        return Cursor(self, self.connPool.pop(i))
        if self.connCount >= 20:
            print("ConnCount exceeded")
            while self.connCount >= 20 and len(self.connPool) == 0:
                sleep(1)
            return self.GetCursor()
        try:
            with self.lock:
                c = Cursor(self, self.CreateConnection())
                self.connCount = self.connCount+1
                return c
        except Exception as e:
            print("Too many connections : " + str(self.connCount))
            raise e
        
                
    
    

class Cursor(object):
    
    def __init__(self, db, conn = None):
        self.cur = None
        self.conn = None
        self.lock = Lock()

        self.lastCmd = None

        self.alive = True
        self.ex = None
        self.commands = []
        self.db = db
        self.lastCmd = None
        self.RefreshConnection(conn, close=False)
            
    def __enter__(self):
        return self
    
    def __exit__(self, type, val, tb):
        self.Close()
        return not type
        
    def __del__(self):
        self.Close()
            
    def Close(self):
        if self.IsClosed():
            if self.conn is not None:
                print("Discarding connection")
                self.conn.close()
                del self.conn
                self.db.connCount = self.db.connCount - 1
        else:
            self.db.connPool.append(self.conn)
        self.conn = None
        self.alive = False
        self.cur = None
        ex = Exception("Cursor has been closed.")
        
    def HasCommands(self):
        return (self.lastCmd is not None and not self.lastCmd[0].lower().strip().startswith("select")) or len(self.commands) > 0
            
        
    def Commit(self):
        if not self.HasCommands():
            return
        if self.IsClosed():
            self.RefreshConnection()
            return self.Commit()
        try:
            ret = self.GetConnection().commit()
            self.ClearCommands()
            return ret
        except Exception:
            self.client.Report(format_exc())
        return self.Commit()
    
    
        
    def IsClosed(self):
        return (not self.alive) or self.conn is None or self.conn.closed != 0
    
    @property
    def closed(self):
        return self.IsClosed()
        
    def ClearCommands(self):
        with self.lock:
            if version_info[0] < 3:
                del self.commands[:]
            else:
                self.commands.clear()
            self.lastCmd = None
        
    def RefreshConnection(self, conn = None, close=True):
        with self.lock:
            if close:
                self.Close()
            if conn is None or conn.closed != 0:
                self.conn = self.db.CreateConnection()
            else:
                self.conn = conn
            self.alive = True
            self.RefreshCursor()
        if len(self.commands) > 0:
            for cmd in self.commands:
                self.Execute(cmd[0], cmd[1])
            if self.lastCmd is not None:
                self.Execute(self.lastCmd[0], self.lastCmd[1])
        return self.conn
        
    def GetConnection(self):
        if self.IsClosed():
            self.Close()
            return self.RefreshConnection()
        return self.conn
        
    def RefreshCursor(self):
        with self.lock:
            self.cur = self.conn.cursor()
            self.alive = True
        
    def FetchOne(self):
        return self.cur.fetchone()
    
    def fetchone(self):
        return self.FetchOne()
    
    def FetchAll(self):
        return self.cur.fetchall()
    
    def GetTextVar(self, name):
        if not isinstance(name, str):
            raise Exception("'name' must be a string'")
        self.Execute("SELECT value FROM TextVars WHERE name=%s LIMIT 1", (name,))
        fVar = self.FetchOne()
        if fVar is None:
            return None
        return fVar[0]
    
    def DeleteTextVar(self, name, commit = True):
        if not isinstance(name, str):
            raise Exception("'name' must be a string'")
        self.Execute("DELETE FROM TextVars WHERE name=%s", (name,))
        if commit:
            self.Commit()
    
    def SetTextVar(self, name, value, commit = True):
        if not isinstance(name, str):
            raise Exception("'name' must be a string'")
        if value is not None:
            value = str(value)
        self.Execute("INSERT INTO TextVars(name, value) Values(%s, %s) ON CONFLICT(name) DO UPDATE SET value=%s", (name, value, value,))
        if commit:
            self.Commit()
            
    def PushCommand(self, cmd, args):
        if self.lastCmd is not None and not self.lastCmd[0].lower().strip().startswith("select"):
            self.commands.append(self.lastCmd)
        self.lastCmd = (cmd, args)
            
    @property
    def rowCount(self):
        return self.cur.rowcount
            
    @property
    def rowcount(self):
        return self.cur.rowcount
    
    def Execute(self, cmd, args=None):
        if True:#with self.db.lock:
            if not self.alive:
                raise self.ex
            try:
                if self.IsClosed():
                    self.Close()
                    self.RefreshConnection()
                ret = None
                if args is None:
                    ret = self.cur.execute(cmd)
                else:
                    ret = self.cur.execute(cmd, args)
                self.PushCommand(cmd, args)
                return ret
            except Exception as ex:
                if self.alive and str(ex).startswith("current transaction is aborted"):
                    self.Close()
                    self.RefreshConnection()
                    self.Execute(cmd, args)
                else:
                    self.Close()
                    self.alive = False
                    self.ex = ex
                    raise ex
                    
    def execute(self, cmd, args=None):
        return self.Execute(cmd, args)
    
    def fetchall(self):
        return self.FetchAll()
