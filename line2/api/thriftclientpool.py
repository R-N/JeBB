from line_0_10_0.TalkService import Client as _Client
from line_0_10_0.ttypes import *
from line2.utils import Lock
from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol import TBinaryProtocol, TProtocol, TCompactProtocol
from thrift.transport import TTransport
from line2.api.thriftclient import ThriftClient

class ThriftClientPool(object):
    def __init__(self, client, url, protocol = TCompactProtocol, urlOut = None, timeout=1000):
        self.timeout = timeout
        self.client = client
        self.url = url
        self.lock = Lock()
        self._protocol = protocol
        self._clients = []
        self._allClients = []
        self._clientCount = 0
        self.timeout = 750
        
    @property
    def _headers(self):
        return self.client._1headers
    
    @property
    def _1headers(self):
        return self.client._1headers
    
    def CloseTransport(self):
        for c in self._allClients:
            try:
                c.CloseTransport()
            except Exception:
                pass
    
    def open(self):
        return self.OpenTransport()
    
    def close(self):
        return self.CloseTransport()
    
    def OpenTransport(self):
        for c in self._allClients:
            try:
                c.OpenTransport()
            except Exception:
                pass
            
    def ReopenTransport(self):
        for c in self._allClients:
            try:
                c.ReopenTransport()
            except Exception:
                pass
    
    def Recreate(self):
        for c in self._allClients:
            try:
                c.Recreate()
            except Exception:
                pass
            
    def setTimeout(self, timeout):
        self.timeout = timeout
        for c in self._allClients:
            try:
                c.setTimeout(timeout)
            except Exception:
                pass
        
    def GetClient(self):
        with self.lock:
            if self._clientCount > 0:
                self._clientCount -= 1
                return self._clients.pop(0)
            #print("CREATING NEW CLIENT")
            ret = ThriftClient(self.client, self.url, protocol=self._protocol, timeout=self.timeout, pool=self)
            ret.setTimeout(self.timeout)
            self._allClients.append(ret)
            return ret
            
    def Add(self, client):
        with self.lock:
            self._clients.append(client)
            self._clientCount +=1
            
    def Remove(self, client):
        with self.lock:
            if client in self._clients:
                self._clientCount -= 1
                self._clients.remove(client)
            
        
    def loginWithIdentityCredentialForCertificate(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.loginWithIdentityCredentialForCertificate(*args, **kwargs)
        
    def loginWithIdentityCredential(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.loginWithIdentityCredential(*args, **kwargs)
        
    def loginWithVerifierForCertificate(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.loginWithVerifierForCertificate(*args, **kwargs)
        
    def getProfile(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getProfile(*args, **kwargs)
        
    def getAllContactIds(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getAllContactIds(*args, **kwargs)
    
    def getContacts(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getContacts(*args, **kwargs)
        
    def findAndAddContactsByMid(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.findAndAddContactsByMid(*args, **kwargs)
        
    def createRoom(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.createRoom(*args, **kwargs)
        
    def getRoom(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getRoom(*args, **kwargs)

    def inviteIntoRoom(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.inviteIntoRoom(*args, **kwargs)

    def leaveRoom(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.leaveRoom(*args, **kwargs)

    def createGroup(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.createGroup(*args, **kwargs)

    def getGroups(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getGroups(*args, **kwargs)

    def getGroupIdsJoined(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getGroupIdsJoined(*args, **kwargs)

    def getGroupIdsInvited(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getGroupIdsInvited(*args, **kwargs)

    def acceptGroupInvitation(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.acceptGroupInvitation(*args, **kwargs)

    def kickoutFromGroup(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.kickoutFromGroup(*args, **kwargs)

    def cancelGroupInvitation(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.cancelGroupInvitation(*args, **kwargs)

    def inviteIntoGroup(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.inviteIntoGroup(*args, **kwargs)

    def leaveGroup(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.leaveGroup(*args, **kwargs)

    def getRecentMessages(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getRecentMessages(*args, **kwargs)
        
    def sendMessage(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.sendMessage(*args, **kwargs)
        
    def getLastOpRevision(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getLastOpRevision()
    

    def fetchOperations(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.fetchOperations(*args, **kwargs)

    def getMessageBoxCompactWrapUp(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getMessageBoxCompactWrapUp(id)

    def getMessageBoxCompactWrapUpList(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getMessageBoxCompactWrapUpList(*args, **kwargs)

    def getRSAKeyInfo(self, *args, **kwargs):
        with self.GetClient() as client:
            return client.getRSAKeyInfo(*args, **kwargs)
        
    def sendChatChecked(self, *args, **kwargs):
        with self.GetClient() as client:
            client.sendChatChecked(*args, **kwargs)