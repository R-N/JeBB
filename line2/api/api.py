# -*- coding: utf-8 -*-
"""
    line.client
    ~~~~~~~~~~~

    LineClient for sending and receiving message from LINE server.

    :copyright: (c) 2014 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""
import ssl

try:
    _create_unverified_https_context = ssl._1create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._1create_default_https_context = _create_unverified_https_context
    
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from rsa import PublicKey, encrypt
from requests import Session, get as RequestsGet, post as RequestsPost
try:
    from simplejson import loads
except ImportError:
    from json import loads
from thrift.transport import TTransport, TSocket
#from thrift.transport import THttpClient
from transport import THttpPersist
from thrift.protocol.TCompactProtocol import TCompactProtocol
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from ssl import SSLError
from thrift.protocol.TProtocol import TProtocolException
from httplib import CannotSendRequest, BadStatusLine, IncompleteRead, ResponseNotReady
from socket import timeout

from traceback import format_exc, print_exc, format_stack

from line_0_10_0.ttypes import *
from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TProtocol
from thriftclient import ThriftClient
from thriftclientpool import ThriftClientPool
from codecs import encode

from line2.utils import Lock, IsEmpty

validContentTypes = [
    ContentType.NONE,
    ContentType.IMAGE,
    ContentType.VIDEO,
    ContentType.AUDIO,
    ContentType.STICKER,
    ContentType.FILE,
    ContentType.CONTACT,
]

needAuthErrors = [
    ErrorCode.AUTHENTICATION_FAILED,
    ErrorCode.NOT_AUTHORIZED_DEVICE,
    ErrorCode.NOT_READY,
    ErrorCode.NOT_AVAILABLE_SESSION,
    ErrorCode.NOT_AUTHORIZED_SESSION,
    ErrorCode.NOT_AUTHENTICATED,
    ErrorCode.INVALID_IDENTITY_CREDENTIAL,
    ErrorCode.NOT_AVAILABLE_IDENTITY_IDENTIFIER,
    ErrorCode.NO_SUCH_IDENTITY_IDENFIER,
    ErrorCode.DEACTIVATED_ACCOUNT_BOUND_TO_THIS_IDENTITY,
    ErrorCode.ILLEGAL_IDENTITY_CREDENTIAL,
    ErrorCode.UNKNOWN_CHANNEL,
    ErrorCode.CHANNEL_DOES_NOT_MATCH,
    ErrorCode.ACCOUNT_NOT_MATCHED,
    ErrorCode.INVALID_SNS_ACCESS_TOKEN,
    ErrorCode.NOT_CERTIFICATED,
    ErrorCode.NOT_ALLOWED_SECONDARY_DEVICE,
    ErrorCode.INVALID_PIN_CODE,
    ErrorCode.NOT_FOUND_IDENTITY_CREDENTIAL,
    ErrorCode.NOT_AVAILABLE_PIN_CODE_SESSION
]

def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num==0) and numerals[0]) or (baseN(num//b, b, numerals).lstrip(numerals[0]) + numerals[num%b])


class LineAPI(object):
    """This class is a wrapper of LINE API

    """
    LINE_DOMAIN = "https://gd2.line.naver.jp"
    LINE_API_VER = 4

    LINE_HTTP_URL = "%s/api/v%d/TalkService.do" % (LINE_DOMAIN, LINE_API_VER) 
    #LINE_HTTP_URL = "%s/api/v%dp/rs" % (LINE_DOMAIN, LINE_API_VER) 
    LINE_HTTP_IN_URL = "%s/P%d" % (LINE_DOMAIN, LINE_API_VER) 
    LINE_HTTP_OUT_URL = "%s/S%d" % (LINE_DOMAIN, LINE_API_VER) 
    LINE_CERTIFICATE_URL = "%s/Q" % LINE_DOMAIN
    LINE_SESSION_LINE_URL = "%s/authct/v1/keys/line" % LINE_DOMAIN
    LINE_SESSION_NAVER_URL = "%s/authct/v1/keys/naver" % LINE_DOMAIN
    
    LINE_PROTOCOL = TCompactProtocol
    if LINE_API_VER == 4:
        LINE_PROTOCOL = TCompactProtocol
    if LINE_API_VER == 3:
        LINE_PROTOCOL = TBinaryProtocol
    
    LINE_TIMELINE_DOMAIN = "https://timeline.line.me"
    LINE_TIMELINE_HTTP_URL = "%s/api" % LINE_TIMELINE_DOMAIN

    ip = "127.0.0.1"


    def __init__(self, client):
        object.__init__(self)
        self.timeout = 1000
        self.client = client
        self._1session = Session()
        self.lock = Lock()
        self._1sessionLock = Lock()
        
    @property
    def _1headers(self):
        return self.client._1headers
        
    @_1headers.setter
    def _1headers(self, value):
        self.client._1headers = value
        
    @property
    def authToken(self):
        return self.client.authToken
    
    @authToken.setter
    def authToken(self, value):
        self.client.authToken = value
        
    @property
    def revision(self):
        return self.client.revision
    
    @revision.setter
    def revision(self, value):
        self.client.revision = value
    
    @property
    def certificate(self):
        return self.client.certificate
    
    @certificate.setter
    def certificate(self, value):
        self.client.certificate = value
    
    @property
    def is_mac(self):
        return self.client.isMac
    
    @is_mac.setter
    def is_mac(self, value):
        self.client.isMac = value
    
    @property
    def provider(self):
        return self.client.provider
    
    @property
    def id(self):
        return self.client.email
    
    @id.setter
    def id(self, value):
        self.client.id = value
    
    @property
    def password(self):
        return self.client.password
    
    @password.setter
    def password(self, value):
        self.client.password = value
        
    @property
    def version(self):
        return self.client.version
        
    @property
    def com_name(self):
        return self.client.comName
        
    @property
    def os_version(self):
        return self.client.osVersion
        

    def ready(self):
        print("READYING")
        with self.lock:
            try:
                self._1client.CloseTransport()
            except Exception:
                pass
            try:
                self._1client_out.CloseTransport()
            except Exception:
                pass
            self._1session.headers.update(self._1headers)
            self._1client = ThriftClientPool(self, self.LINE_HTTP_IN_URL, protocol = self.LINE_PROTOCOL)
            self._1client_out = ThriftClientPool(self, self.LINE_HTTP_OUT_URL, protocol=self.LINE_PROTOCOL)
            #self._1client_out = self._1client
            
    def open(self):
        with self.lock:
            self._1client.open()
            #self._1client_out.open()
        
    def close(self):
        with self.lock:
            self._1client.close()
            #self._1client_out.close()
        
    def setTimeout(self, timeout):
        with self.lock:
            self.timeout = timeout
            self._1client.setTimeout(timeout)
            #self._1client_out.setTimeout(timeout+1000)

    def updateAuthToken(self):
        """
        After login, update authToken to avoid expiration of
        authToken. This method skip the PinCode validation step.
        """
        with self.lock:
            print("UPDATEAUTH HEADERS " + str(self._1headers))
            if self.certificate:
                self.login(False)
                self.ready()

                return True
            else:
                raise Exception("You need to login first. There is no valid certificate.\nCert0:'" + str(self.certificate) + "'\nToken:'" + str(self.authToken))

    def tokenLogin(self):
        with self.lock:
            print("TOKENLOGIN")
            self.ready()
            return

    def login(self, firstLogin = False):
        """Login to LINE server."""
        with self.lock:
            if self.provider == IdentityProvider.LINE: # LINE
                j = self._1get_json(self.LINE_SESSION_LINE_URL)
            else: # NAVER
                j = self._1get_json(self.LINE_SESSION_NAVER_URL)
            #self.transport.setCustomHeaders(self._1headers)
            prov = self.provider
            cert = self.certificate
            id = self.id
            password = self.password
            
            if firstLogin:
                cert = ""
            #if not IsEmpty(self.authToken):
                #pass
                #prov = 0
                #id = None
                #password = None

            if self.authToken is None:
                self._1headers['X-Line-Application'] = self.client.loginApp
                self._1client = ThriftClient(self, self.LINE_HTTP_URL, protocol=self.LINE_PROTOCOL)
            else:
                self._1headers['X-Line-Application'] = self.client.app
                self._1client = ThriftClient(self, self.LINE_HTTP_IN_URL, protocol=self.LINE_PROTOCOL)
                
            #key = self._1client.getRSAKeyInfo(prov)

            session_key = j['session_key']
            message = encode(chr(len(session_key)) + session_key + chr(len(self.id)) + self.id + chr(len(self.password)) + self.password, 'utf-8')

            keyname, n, e = j['rsa_key'].split(",")
            pub_key = PublicKey(int(n,16), int(e,16))
            en = encrypt(message, pub_key)
            #crypto = str(encode(en, 'hex'), 'utf-8')
            crypto = str(encode(en, 'hex'))
            
            #message2 = encode(chr(len(key.sessionKey)) + key.sessionKey + chr(len(self.id)) + self.id + chr(len(self.password)) + self.password, 'utf-8')
            #pub_key2 = PublicKey(int(key.nvalue,16), int(key.evalue,16))
            #en2 = encrypt(message2, pub_key2)
            #crypto2 = str(encode(en2, 'hex'))
            
            #print("KEYNAME " + str(keyname))
            #print("CRYPTO " + str(crypto))
            #print("KEYNM " + str(key.keynm))
            #print("CRYPTO2 " + str(crypto2))
                
            #print ("LOGGING IN HEADERS " + str(self._1headers))
            #msg = self._1client.loginWithIdentityCredential(prov, id, password, True, self.ip, self.com_name, cert)
            #msg = self._1client.loginWithIdentityCredentialForCertificate(prov, id, password, True, self.ip, self.com_name, cert)
            msg = self._1client.loginWithIdentityCredentialForCertificate(prov, keyname, crypto, True, self.ip, self.com_name, cert)
            #msg = self._1client.loginWithIdentityCredentialForCertificate(prov, key.keynm, crypto2, True, self.ip, self.com_name, cert)
            #msg = self._1client.loginWithIdentityCredentialForCertificate(id, password, keyname, crypto, True, self.ip, self.com_name, prov, cert)
            #msg = self._1client.loginWithIdentityCredentialForCertificate(id, password, key.keynm, crypto2, True, self.ip, self.com_name, prov, cert)

            if msg.type == 1:
                if not IsEmpty(msg.certificate):
                    self.certificate = msg.certificate
                self.authToken = self._1headers['X-Line-Access'] = msg.authToken
            elif msg.type == 2:
                msg = "require QR code"
                raise Exception(msg)
            elif msg.type == 3:
                self.verifier = self._1headers['X-Line-Access'] = msg.verifier
                pinCode = str(msg.pinCode)
                print("VERIFIER " + str(self.verifier))
                print("PINCODE " + pinCode)
                return pinCode
                self.resumeLogin()

                #raise Exception("Code is removed because of the request of LINE corporation")
            elif not (msg.authToken and msg.authToken.strip()):
                self.authToken = self._1headers['X-Line-Access'] = msg.authToken

        
    def resumeLogin(self):
        with self.lock:
            print("RESUME LOGIN")
            j = self.get_json(self.LINE_CERTIFICATE_URL)
            self.verifier = j['result']['verifier']
            

            msg = self._1client.loginWithVerifierForCertificate(self.verifier)
            if msg.type == 1:
                print("MSG TYPE 1")
                if msg.certificate is not None:
                    print("SETTING CERT")
                    self.certificate = msg.certificate
                    #f = cStringIO.StringIO()
                    #f.write(msg.certificate)
                    #f.seek(0)
                    #self.certificate = f.read()
                    #f.close()
                    #print("Cert2 : '" + str(self.certificate) + "'")
                if msg.authToken is not None:
                    print("SETTING AUTH")
                    self.authToken = self._1headers['X-Line-Access'] = msg.authToken
                    return True
                else:
                    return False
            else:
                msg = "Require device confirm"
                raise Exception(msg)
            return False

    def get_json(self, url):
        """Get josn from given url with saved session and headers"""
        with self._1sessionLock:
            return loads(self._1session.get(url, headers=self._1headers).text)
    
    def ReopenTransport(self):
        with self.lock:
            self.close()
            self.setTimeout(self.timeout)
            self.open()

    def _1getProfile(self):
        """Get profile information

        :returns: Profile object
                    - picturePath
                    - displayName
                    - phone (base64 encoded?)
                    - allowSearchByUserid
                    - pictureStatus
                    - userid
                    - mid # used for unique mid for account
                    - phoneticName
                    - regionCode
                    - allowSearchByEmail
                    - email
                    - statusMessage
        """
        return self._1client.getProfile()

    def _1getAllContactIds(self):
        """Get all contacts of your LINE account"""
        return self._1client.getAllContactIds()

    def _1getContacts(self, mids):
        """Get contact information list from mids

        :returns: List of Contact list
                    - status
                    - capableVideoCall
                    - dispalyName
                    - settings
                    - pictureStatus
                    - capableVoiceCall
                    - capableBuddy
                    - mid
                    - displayNameOverridden
                    - relation
                    - thumbnailUrl
                    - createdTime
                    - facoriteTime
                    - capableMyhome
                    - attributes
                    - type
                    - phoneticName
                    - statusMessage
        """
        if type(mids) != list:
            msg = "argument should be list of contact mids"
            raise Exception(msg)
        return self._1client.getContacts(mids)

    def _1findAndAddContactsByMid(self, mids, seq=0):
        """Find and add contacts by Mid"""
        return self._1client_out.findAndAddContactsByMid(seq, mids)

    def _1createRoom(self, mids, seq=0):
        """Create a chat room"""
        return self._1client_out.createRoom(seq, mids)

    def _1getRoom(self, mid):
        """Get a chat room"""
        return self._1client.getRoom(mid)

    def _1inviteIntoRoom(self, roomId, contactIds=[]):
        """Invite contacts into room"""
        return self._1client_out.inviteIntoRoom(0, roomId, contactIds)

    def _1leaveRoom(self, mid):
        """Leave a chat room"""
        return self._1client_out.leaveRoom(0, mid)

    def _1createGroup(self, name, mids, seq=0):
        """Create a group"""
        return self._1client_out.createGroup(seq, name, mids)

    def _1getGroups(self, mids):
        """Get a list of group with mids"""
        if type(mids) != list:
            msg = "argument should be list of group mids"
            raise Exception(msg)

        return self._1client.getGroups(mids)

    def _1getGroupIdsJoined(self):
        """Get group mid that you joined"""
        return self._1client.getGroupIdsJoined()

    def _1getGroupIdsInvited(self):
        """Get group mid that you invited"""
         
        return self._1client.getGroupIdsInvited()

    def _1acceptGroupInvitation(self, groupId, seq=0):
        """Accept a group invitation"""
        return self._1client_out.acceptGroupInvitation(seq, groupId)

    def _1kickoutFromGroup(self, groupId, contactIds=[], seq=0):
        """Kick a group members"""
        return self._1client_out.kickoutFromGroup(seq, groupId, contactIds)

    def _1cancelGroupInvitation(self, groupId, contactIds=[], seq=0):
        """Cancel a group invitation"""
        return self._1client_out.cancelGroupInvitation(seq, groupId, contactIds)

    def _1inviteIntoGroup(self, groupId, contactIds=[], seq=0):
        """Invite contacts into group"""
        return self._1client_out.inviteIntoGroup(seq, groupId, contactIds)

    def _1leaveGroup(self, mid):
        """Leave a group"""
        return self._1client_out.leaveGroup(0, mid)

    def _1getRecentMessages(self, mid, count=1):
        """Get recent messages from `id`"""
        return self._1client.getRecentMessages(mid, count)
    
    
    def _1sendChatChecked(self, target, msgid, seq=0):
        return self._1client_out.sendChatChecked(seq, target, msgid)

    def _1sendMessage(self, message, seq=0, exceptionLevel = 2):
        """Send a message to `id`. `id` could be contact mid or group mid

        :param message: `message` instance
        """
        return self._1client_out.sendMessage(seq, message, exceptionLevel = exceptionLevel)

    def _1getLastOpRevision(self):
        return self._1client.getLastOpRevision()
    

    def _1fetchOperations(self, revision, count=50, tries=1):
        return self._1client.fetchOperations(revision, count, checkReturn = False, exceptionLevel = 0, tries=tries)

    def _1getMessageBoxCompactWrapUp(self, mid):
        try:
            return self._1client.getMessageBoxCompactWrapUp(mid)
        except Exception:
            return None

    def _1getMessageBoxCompactWrapUpList(self, start=1, count=50):
        return self._1client.getMessageBoxCompactWrapUpList(start, count)
    
    def post(self, url, data=None, json=None, **kwargs):
        return self._1session.post(url, data, json, **kwargs)
    
    def get(self, url, **kwargs):
        return self._1session.get(url, **kwargs)
    
    def head(self, url, **kwargs):
        return self._1session.head(url, **kwargs)
    
    def request(self, *args, **kwargs):
        return self._1session.request(*args, **kwargs)

    def _1get_json(self, url):
        """Get josn from given url with saved session and headers"""
        #with self._1sessionLock:
        #    return loads(self._1session.get(url, headers=self._1headers).text)
        return loads(RequestsGet(url, headers=self._1headers).text)

    def post_content(self, url, data=None, files=None):
        #with self._1sessionLock:
        #    return self._1session.post(url, headers=self._1headers, data=data, files=files)
        return RequestsPost(url, headers=self._1headers, data=data, files=files)
