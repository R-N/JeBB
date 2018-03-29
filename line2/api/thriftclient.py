from line_0_10_0.TalkService import Client as _Client
#from login import Client as _Client
from line_0_10_0.ttypes import *
from line2.utils import Lock
from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol import TBinaryProtocol, TProtocol, TCompactProtocol
from thrift.transport import TTransport
from transport import THttpPersist
from ssl import SSLError
from thrift.protocol.TProtocol import TProtocolException
from httplib import CannotSendRequest, BadStatusLine, IncompleteRead, ResponseNotReady
from socket import timeout
from time import time


class ThriftClient(object):
    def __init__(self, client, url, protocol = TCompactProtocol, urlOut = None, timeout=1000, pool = None):
        self.timeout = timeout
        self.client = client
        self.url = url
        self.urlOut = urlOut
        self.lock = Lock()
        self._protocol = protocol
        self.pool = pool
        self.Recreate()
            
    def __enter__(self):
        with self.lock:
            #if self.pool:
            #    self.pool.Remove(self)
            return self
    
    def __exit__(self, type, val, tb):
        with self.lock:
            if not self.clear:
                self.reopen()
            if not self.clear:
                if self.pool:
                    self.close()
                    self.pool._allClients.remove(self)
                else:
                    assert self.clear
            elif self.pool:
                self.pool.Add(self)
        return not type
                
    @property
    def clear(self):
        return self.protocol.state == 0 and (self.protocol_out is None or self.protocol_out.state == 0)
        
    def ExceptionHandler(self, method, *args, **kwargs):
        with self.lock:
            exceptionLevel = kwargs.pop('exceptionLevel', 2)
            checkReturn = kwargs.pop('checkReturn', False)
            tries = kwargs.pop('tries', 3)
            if exceptionLevel > 3:
                return method(*args, **kwargs)
            for i in range(0, 2):
                for j in range(0, tries):
                    reopened = False
                    try:
                        ret = method(*args, **kwargs)
                        if (not checkReturn) or ret is not None:
                            return ret
                    except (CannotSendRequest, BadStatusLine, IncompleteRead, ResponseNotReady, TApplicationException):
                        self.reopen()
                        reopened = True
                    except AssertionError:
                        self.reopen()
                        reopened=True
                    except SSLError as e:
                        if e[0] == 'The read operation timed out':
                            pass
                        elif e[0] == '_ssl.c:645: The handshake operation timed out':
                            self.reopen()
                            reopened = True
                    except timeout:
                        pass
                    except (EOFError, AttributeError, TProtocolException):
                        pass
                    except TalkException as e:
                        raise
                    except Exception as e:
                        if exceptionLevel < 2:
                            print_exc()
                            pass
                        else:
                            raise
                if not self.clear and not reopened:
                    self.reopen()
                    reopened=True
            if exceptionLevel > 0:
                if not self.pool:
                    return method(*args, **kwargs)
                kwargs['exceptionLevel'] = 0
                kwargs['checkReturn'] = checkReturn
                kwargs['tries'] = tries
                with self.pool.GetClient() as client:
                    m = method.__get__(client)
                    return client.ExceptionHandler(m, *args, **kwargs)
        
    @property
    def _1headers(self):
        return self.client._1headers
    
    @property
    def _headers(self):
        return self.client._1headers
    
    def OpenTransport(self):
        with self.lock:
            if self.transport_out:
                return self.transport.open() and self.transport_out.open()
            return self.transport.open()
        
    def open(self):
        return self.OpenTransport()
    
    
    def CloseTransport(self):
        with self.lock:
            if self.transport_out:
                return self.transport.close() and self.transport_out.close()
            return self.transport.close()
        
    def close(self):
        return self.CloseTransport()
        
    def ReopenTransport(self):
        with self.lock:
            self.setTimeout(self.timeout)
            if not self.clear:
                self.Recreate()
            return self.clear
        
    def reopen(self):
        return self.ReopenTransport()
        
    def Recreate(self):
        with self.lock:
            try:
                self.CloseTransport()
            except Exception:
                pass
            
            self.transport = THttpPersist(self.url)
            self.transport.setCustomHeaders(self._1headers)
            self.protocol = self._protocol(self.transport)
            self.protocol.state = 0
            if self.urlOut:
                self.transport_out = THttpPersist(self.urlOut)
                self.protocol_out = self._protocol(self.transport_out)
                self.protocol_out.state = 0
            else:
                self.transport_out = None
                self.protocol_out = None
            self._client = _Client(self.protocol, self.protocol_out)
            if self.transport_out:
                self.transport_out.open()
            self.transport.open()
            self.setTimeout(self.timeout)
            
    
    def setTimeout(self, timeout):
        self.timeout = timeout
        with self.lock:
            self.close()
            self.transport.setTimeout(timeout)
            if self.transport_out:
                self.transport_out.setTimeout(timeout)
            self.open()
        
        
    def loginWithIdentityCredentialForCertificate(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.loginWithIdentityCredentialForCertificate, *args, **kwargs)
        
        
    def loginWithIdentityCredential(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.loginWithIdentityCredential, *args, **kwargs)
        
    def loginWithVerifierForCertificate(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.loginWithVerifierForCertificate, *args, **kwargs)
        
    def getProfile(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getProfile, *args, **kwargs)
        
    def getAllContactIds(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getAllContactIds, *args, **kwargs)
    
    def getContacts(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getContacts, *args, **kwargs)
        
    def findAndAddContactsByMid(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.findAndAddContactsByMid, *args, **kwargs)
        
    def createRoom(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.createRoom, *args, **kwargs)
        
    def getRoom(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getRoom, *args, **kwargs)

    def inviteIntoRoom(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.inviteIntoRoom, *args, **kwargs)

    def leaveRoom(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.leaveRoom, *args, **kwargs)

    def createGroup(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.createGroup, *args, **kwargs)

    def getGroups(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getGroups, *args, **kwargs)

    def getGroupIdsJoined(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getGroupIdsJoined, *args, **kwargs)

    def getGroupIdsInvited(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getGroupIdsInvited, *args, **kwargs)

    def acceptGroupInvitation(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.acceptGroupInvitation, *args, **kwargs)

    def kickoutFromGroup(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.kickoutFromGroup, *args, **kwargs)

    def cancelGroupInvitation(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.cancelGroupInvitation, *args, **kwargs)

    def inviteIntoGroup(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.inviteIntoGroup, *args, **kwargs)

    def leaveGroup(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.leaveGroup, *args, **kwargs)

    def getRecentMessages(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getRecentMessages, *args, **kwargs)
        
    def sendMessage(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.sendMessage, *args, **kwargs)
        
    def getLastOpRevision(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getLastOpRevision, *args, **kwargs)
    

    def fetchOperations(self, *args, **kwargs):
        with self.lock:
            #then = time()
            return self.ExceptionHandler(self._client.fetchOperations, *args, **kwargs)
            #print("FETCHOPERATIONS %g" % (time() - then))
            #return ret

    def getMessageBoxCompactWrapUp(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getMessageBoxCompactWrapUp, *args, **kwargs)

    def getMessageBoxCompactWrapUpList(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getMessageBoxCompactWrapUpList, *args, **kwargs)
        
    def sendChatChecked(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.sendChatChecked, *args, **kwargs)
    
    def getRSAKeyInfo(self, *args, **kwargs):
        with self.lock:
            return self.ExceptionHandler(self._client.getRSAKeyInfo, *args, **kwargs)

    @property
    def _oprot(self):
        with self.lock:
            return self._client._oprot
    @property
    def _iprot(self):
        with self.lock:
            return self._client._iprot
    @property
    def _seqid(self):
        with self.lock:
            return self._client._seqid
        