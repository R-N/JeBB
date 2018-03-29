
from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
import sys
import logging
from line_0_10_0.ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from line_0_10_0.TalkService import Client as _Client
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None

class loginWithIdentityCredentialForCertificate_args(object):
  """
  Attributes:
   - identifier
   - password
   - keyname
   - crypto
   - keepLoggedIn
   - accessLocation
   - systemName
   - identityProvider
   - certificate
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'identifier', None, None, ), # 1
    (2, TType.STRING, 'password', None, None, ), # 2
    (3, TType.STRING, 'keyname', None, None, ), # 3
    (4, TType.STRING, 'crypto', None, None, ), # 4
    (5, TType.BOOL, 'keepLoggedIn', None, None, ), # 5
    (6, TType.STRING, 'accessLocation', None, None, ), # 6
    (7, TType.STRING, 'systemName', None, None, ), # 7
    (8, TType.I32, 'identityProvider', None, None, ), # 8
    (9, TType.STRING, 'certificate', None, None, ), # 9
  )

  def __init__(self, identifier=None, password=None, keyname=None, crypto=None, keepLoggedIn=None, accessLocation=None, systemName=None, identityProvider=None, certificate=None,):
    self.identifier = identifier
    self.password = password
    self.keyname = keyname
    self.crypto = crypto
    self.keepLoggedIn = keepLoggedIn
    self.accessLocation = accessLocation
    self.systemName = systemName
    self.identityProvider = identityProvider
    self.certificate = certificate

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.identifier = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.password = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.keyname = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.crypto = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.BOOL:
          self.keepLoggedIn = iprot.readBool();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.STRING:
          self.accessLocation = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.STRING:
          self.systemName = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.I32:
          self.identityProvider = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.STRING:
          self.certificate = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('loginWithIdentityCredentialForCertificate_args')
    if self.identifier is not None:
      oprot.writeFieldBegin('identifier', TType.STRING, 1)
      oprot.writeString(self.identifier)
      oprot.writeFieldEnd()
    if self.password is not None:
      oprot.writeFieldBegin('password', TType.STRING, 2)
      oprot.writeString(self.password)
      oprot.writeFieldEnd()
    if self.keyname is not None:
      oprot.writeFieldBegin('keyname', TType.STRING, 3)
      oprot.writeString(self.keyname)
      oprot.writeFieldEnd()
    if self.crypto is not None:
      oprot.writeFieldBegin('crypto', TType.STRING, 4)
      oprot.writeString(self.crypto)
      oprot.writeFieldEnd()
    if self.keepLoggedIn is not None:
      oprot.writeFieldBegin('keepLoggedIn', TType.BOOL, 5)
      oprot.writeBool(self.keepLoggedIn)
      oprot.writeFieldEnd()
    if self.accessLocation is not None:
      oprot.writeFieldBegin('accessLocation', TType.STRING, 6)
      oprot.writeString(self.accessLocation)
      oprot.writeFieldEnd()
    if self.systemName is not None:
      oprot.writeFieldBegin('systemName', TType.STRING, 7)
      oprot.writeString(self.systemName)
      oprot.writeFieldEnd()
    if self.identityProvider is not None:
      oprot.writeFieldBegin('identityProvider', TType.I32, 8)
      oprot.writeI32(self.identityProvider)
      oprot.writeFieldEnd()
    if self.certificate is not None:
      oprot.writeFieldBegin('certificate', TType.STRING, 9)
      oprot.writeString(self.certificate)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class loginWithIdentityCredentialForCertificate_result(object):
  """
  Attributes:
   - success
   - e
  """

  thrift_spec = (
    (0, TType.STRUCT, 'success', (LoginResult, LoginResult.thrift_spec), None, ), # 0
    (1, TType.STRUCT, 'e', (TalkException, TalkException.thrift_spec), None, ), # 1
  )

  def __init__(self, success=None, e=None,):
    self.success = success
    self.e = e

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.STRUCT:
          self.success = LoginResult()
          self.success.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 1:
        if ftype == TType.STRUCT:
          self.e = TalkException()
          self.e.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('loginWithIdentityCredentialForCertificate_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.STRUCT, 0)
      self.success.write(oprot)
      oprot.writeFieldEnd()
    if self.e is not None:
      oprot.writeFieldBegin('e', TType.STRUCT, 1)
      self.e.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Client(_Client):
  def __init__(self, iprot, oprot=None):
    _Client.__init__(self, iprot, oprot)

  def loginWithIdentityCredentialForCertificate(self, identifier, password, keyname, crypto, keepLoggedIn, accessLocation, systemName, identityProvider, certificate):
    """
    Parameters:
     - identifier
     - password
     - keyname
     - crypto
     - keepLoggedIn
     - accessLocation
     - systemName
     - identityProvider
     - certificate
    """
    self.send_loginWithIdentityCredentialForCertificate(identifier, password, keyname, crypto, keepLoggedIn, accessLocation, systemName, identityProvider, certificate)
    return self.recv_loginWithIdentityCredentialForCertificate()

  def send_loginWithIdentityCredentialForCertificate(self, identifier, password, keyname, crypto, keepLoggedIn, accessLocation, systemName, identityProvider, certificate):
    self._oprot.writeMessageBegin('loginWithIdentityCredentialForCertificate', TMessageType.CALL, self._seqid)
    args = loginWithIdentityCredentialForCertificate_args()
    args.identifier = identifier
    args.password = password
    args.keyname = keyname
    args.crypto = crypto
    args.keepLoggedIn = keepLoggedIn
    args.accessLocation = accessLocation
    args.systemName = systemName
    args.identityProvider = identityProvider
    args.certificate = certificate
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

  def recv_loginWithIdentityCredentialForCertificate(self):
    (fname, mtype, rseqid) = self._iprot.readMessageBegin()
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(self._iprot)
      self._iprot.readMessageEnd()
      raise x
    result = loginWithIdentityCredentialForCertificate_result()
    result.read(self._iprot)
    self._iprot.readMessageEnd()
    if result.success is not None:
      return result.success
    if result.e is not None:
      raise result.e
    raise TApplicationException(TApplicationException.MISSING_RESULT, "loginWithIdentityCredentialForCertificate failed: unknown result");