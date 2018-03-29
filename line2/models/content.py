from requests import Session, get as RequestsGet
from io import BytesIO
from line2.utils import IsEmpty, Lock
        
def ReadContent(content):
    b = bytes()
    for chunk in content.iter_content():
        b = b + bytes(chunk)
    return b

def ReadStream(stream):
    return stream.read()

def Download(url, headers={}):
    r0 = RequestsGet(url, headers=headers)
    if r0.status_code != 200:
        return
    b = bytes()
    for chunk in r0:
        b = b + bytes(chunk)
    return b

def ScaleyUrl(url, max=1024):
    return "https://i.scaley.io/" + str(max) + "-max/" + url.replace("https://", "http://") 
    

def UploadPyImgur(client, bytes):
    if client is None:
        raise Exception("[UploadPYImgur] Please give client")
    if bytes is None:
        raise Exception("[UploadPYImgur] Please give 'bytes'")
    r = client._send_request('https://api.imgur.com/3/image', method='POST', params={'image': bytes})
    link = r['link'].replace("http:", "https:")
    return link

global defaultClient
defaultClient = None



class Content(object):
    def __init__(self, client=None, message=None, url = None, bytes = None, hasOA=False, hasUser=False):
        self.lock = Lock()
        self._1message=message
        if client is None and message:
            client = message.client
        global defaultClient
        if client:
            defaultClient = client
        else:
            client = defaultClient
        self.client = client
        if url is None and id is not None and self.hasUser:
            url = "http://os.line.naver.jp/os/m/" + str(id)
        self._1url = url
        self._1bytes = bytes
        
    @property
    def hasUser(self):
        if self.message is not None:
            return self.message.hasUser
        return False
    
    @property
    def hasOA(self):
        if self.message is not None:
            return self.message.hasOA
        return False
        
    def GetContent(self):
        with self.lock:
            if self.message:
                self._1bytes = self.message.GetContent()
            return self._1bytes
            
    @property
    def message(self):
        return self._1message
    
    @message.setter
    def message(self, value):
        with self.lock:
            self._1message = value
            self._1bytes = None
            self._1url = None
        
    @property
    def id(self):
        return self._1message.id
        
    @property
    def url(self):
        with self.lock:
            if self._1url is None and self.bytes is not None:
                self._1url = self.UploadPyImgur()
            return self._1url
    
    @url.setter
    def url(self, value):
        with self.lock:
            self._1url = value
            self._1bytes = None
            self._1message = None
        
    @property
    def bytes(self):
        with self.lock:
            if self._1bytes is None:
                if self.hasOA:
                    self._1bytes = self.GetContent()
                elif self._1url is not None:
                    self._1bytes = self.Download()
            return self._1bytes
    
    @bytes.setter
    def bytes(self, value):
        with self.lock:
            self._1bytes = value
            self._1url = None
            self._1message = None
        
    def Download(self):
        with self.lock:
            self._1bytes = Download(self.url, headers=self.client._1headers)
            return self._1bytes
    
    @property
    def stream(self):
        return BytesIO(self.bytes)
    
    @stream.setter
    def stream(self, value):
        with self.lock:
            self.bytes = value.read()
    
    def open(self):
        return self.stream
    
    @property
    def file(self):
        return self.stream
    
class Image(Content):
    
    def ScaleyURL(url, max=1024):
        return ScaleyURL(self.url, max)
    
    @property
    def imgurUrl(self):
        with self.lock:
            if not IsEmpty(self.url) and self._1url.startswith("https://i.imgur"):
                return self._1url
            self._1url = self.UploadPyImgur()
            return self._1url

    def UploadPyImgur(self):
        with self.lock:
            if self.client.pyImgurKey is not None:
                self._1url = UploadPyImgur(self.client.GetPyImgurClient(), bytes=self.bytes)
                return self._1url
class File(Content):
    pass