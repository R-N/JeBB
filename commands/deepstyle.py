from line2.models.command import ImageCommand, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty
from line2.models.content import Image
from re import compile, DOTALL
from requests import Session
from utils import WaitOK

from fake_useragent import UserAgent

dsTokenRx = compile('.*"_token" +value="([^"]+)"', DOTALL)
dsLinkRx = compile('.*< *img +id *= *"dream-image" +class *= *"img-responsive" +src *= *"([^"]+)"', DOTALL)
dsLinkParseRx = compile('https*://([^/]+)(.*)$', DOTALL)
dsErrorRx = compile('.*<p class="alert alert-info text-center">([^<]+)<', DOTALL)


dsEmail = ""
dsPw = ""
dsLoginUrl = "https://deepdreamgenerator.com/login"
dsUrl = "https://deepdreamgenerator.com/generator-style"
dsUploadUrl = "https://deepdreamgenerator.com/upload-image"

def TryChangeToken(text, info):
    mToken = dsTokenRx.match(text)
    if mToken is not None:
        token = mToken.group(1)
        info["_token"] = token
        

def DeepStyle(message, options, images=[]):
    print("Getting session")
    s = Session()
    s.auth = (dsEmail, dsPw)
    s.headers.update({'User-Agent' : str(UserAgent().chrome)})
    print("Getting token")
    rToken = s.get(dsLoginUrl)
    if rToken.status_code != 200:
        message.ReplyText("Error DS 1")
        return CommandResult.Failed()
    mToken = dsTokenRx.match(rToken.text)


    token = mToken.group(1)
    info = {"_token":token, "email":dsEmail, "password":dsPw, "remember":"true"}
    
    print("Logging in")
    rLogin = s.post(dsLoginUrl, data=info)
    if rLogin.status_code != 200:
        message.ReplyText("Error DS 2")
        return CommandResult.Failed()
    TryChangeToken(rLogin.text, info)
    rDeepStyle = s.get(dsUrl, data=info)
    if rDeepStyle.status_code != 200:
        message.ReplyText("Error DS 3")
        return CommandResult.Failed()
    info = {"_token":info["_token"]}
    TryChangeToken(rDeepStyle.text, info)
    print("Getting images")
    style = images[0].bytes
    img = images[1].bytes
    print("Requesting deepstyle")
    info["style"] = "custom"
    info["dreamType"]="deep-style"
    info["resolution"]="normal"
    info["optimizer"]="alpha"
    info["iterationsDepth"] ="normal"
    info["preserveOriginalColors"]="no"
    info["access"] = "public"
    info["styleScale"] = "1"
    info["styleWeight"] = "5"
    rUploadImg = s.post(dsUploadUrl, data=info, files={'image':img, 'styleImage':style})
    if rUploadImg.status_code != 200:
        message.ReplyText("Error DS 4\n" + rUploadImg.text)
        return CommandResult.Failed()
    
    mDsLink = dsLinkRx.match(rUploadImg.text)
    if mDsLink is None:
        message.ReplyText("Error DS 5 : '" + dsErrorRx.match(rUploadImg.text).group(1).replace('&quot;', '"') + "'")
        return CommandResult.Failed()
        while mDsLink is None:
            time.sleep(300)
            rUploadImg = s.post(dsUploadUrl, data=info, files={'image':img, 'styleImage':style})
            if rUploadImg.status_code != 200:
                message.ReplyText("Error DS 6")
                return CommandResult.Failed()
            mDsLink = dsLinkRx.match(rUploadImg.text)
            
    dsLink = mDsLink.group(1)
    message.ReplyText("[DeepStyle] Please wait up to 5 minutes\n" + dsLink)
    mDsLinkParse = dsLinkParseRx.match(dsLink)
    host = mDsLinkParse.group(1)
    path = mDsLinkParse.group(2)
    WaitOK(host, path)
    img = Image(url=dsLink)
    return CommandResult.Done(images=[img])

deepStyleCmd = ImageCommand(
    'deepstyle',
    DeepStyle,
    desc='Transfer style from an image to another',
    images=['image to transfer style from', 'image to transfer style to']
)
