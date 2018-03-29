from line2.models.command import HybridCommand, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty
from line2.models.content import Image
from requests import post, Session
from utils import WaitOK
from re import compile, DOTALL
from json import loads
from time import sleep

imagesStr=['image to transfer style from', 'image to transfer style to']

def DeepArtBuiltin(message, style, images):
    if not style.isdigit():
        message.ReplyText("Invalid style (1)")
        return CommandResult.Failed()
    r = post('http://turbo.deepart.io/api/post/',
                      data={
                            'style': style,
                            'return_url': 'http://my.return/' 
                      },
                      files={ 
                            'input_image': (
                                'file.jpg', 
                                images[0].bytes, 
                                'image/jpeg' 
                            ) 
                      } 
            )
    
    img=r.text
    if len(img) > 100:
        message.ReplyText("Invalid style (2)")
        return CommandResult.Failed()
    
    path=("/media/output/%s.jpg" % img)
    link = "https://turbo.deepart.io" + path
    message.ReplyText("[DeepArt] Please wait up to 3 minutes.\n" + link)
    WaitOK("turbo.deepart.io", path)
    img = Image(url=link)
    return CommandResult.Done(images=[img])
    
        
daLoginUrl = "https://deepart.io/login/"
daUrl = "https://deepart.io/hire/"
daContentUploadUrl = "https://deepart.io/image/upload/content"
daStyleUploadUrl = "https://deepart.io/image/upload/style"
daHomeUrl = 'https://deepart.io'
daHost = 'https://deepart.io/img/'
daTokenRx = compile(".*name *= *'csrfmiddlewaretoken' +value *= *'([^']+)'", DOTALL)
daCodeRx = compile('.*?class *= *"row submissions submission likes" +id *= *"([^"]+)"', DOTALL)
daImgRx = compile('.*?<meta +property *= *"og:image" +content *= *"([^"]+)"', DOTALL)
daEmail = ''
daPw = ''

def DeepArtCustom(message, images):
    s = Session()
    print("Getting token ...")
    rToken = s.get(daLoginUrl, verify=False)
    mToken = daTokenRx.match(rToken.text)
    token = mToken.group(1)

    print("Logging in ...")
    info = {'csrfmiddlewaretoken' : token,
           'email' : daEmail,
           'password' : daPw}
    rLogin = s.post(daLoginUrl, verify=False)

    print("Uploading image ...")
    img = images[1].bytes
    rImg = s.post(daContentUploadUrl, files={'image':img}, verify=False)
    jImg = loads(rImg.text)

    print("Uploading style ...")
    style = images[0].bytes
    rStyle = s.post(daStyleUploadUrl, files={'image':style}, verify=False)
    jStyle = loads(rStyle.text)

    print("Requesting ...")
    info = {'content_img':jImg['hash'],
           'style_img':jStyle['hash'],
           'email':daEmail,
           'password':daPw,
            'privacy':'private'
           }

    rDa = s.post(daUrl, data=info, verify=False)
    jDa = loads(rDa.text)
    rDa = s.post(daHomeUrl + jDa['redirect'], verify=False)
    mDaCode = daCodeRx.match(rDa.text)
    daCode = mDaCode.group(1)
    daCodeUrl = daHost + daCode + "/"
    message.ReplyText("[DeepArt] Please wait up to 15 minutes.\n" + daCodeUrl)
    while True:
        rDaCode = s.get(daCodeUrl, verify=False)
        if rDaCode.url == daCodeUrl:
            mDaImg = daImgRx.match(rDaCode.text)
            daImg = mDaImg.group(1)
            img = Image(url=daImg)
            return CommandResult.Done(images=[img])
        sleep(5)

def DeepArt(message, options, text='', style='', images=[]):
    if IsEmpty(style):
        style = text
    if IsEmpty(style):
        style = 'custom'
    imageLen = len(images)
    if style == 'custom':
        if imageLen < 2:
            return CommandResult.ExpectImage(askImage=imagesStr[imageLen])
        return DeepArtCustom(message, images)
    else:
        if imageLen == 0:
            return CommandResult.ExpectImage(askImage=imagesStr[1])
        return DeepArtBuiltin(message, style, images)

deepArtCmd = HybridCommand(
    'deepart',
    DeepArt,
    desc='Change image style',
    images=imagesStr
)
