from line2.models.command import ImageCommand, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty
from utils import Tint
from io import BytesIO
from line2.models.content import Image
from PIL import Image as PILImage, ImageFilter, ImageOps, ImageEnhance, ImageColor, ImageChops

def DeepFry(message, options, images=[], quality=90, iterations=3, pixel=0.95, iterations2=3, tint="rgb(255,160,100)"):
    img = images[0].bytes
    imgIn = BytesIO(img)
    
    baseQuality=quality
    scale = pixel
    secondIter=iterations2
    tintColor = tint
    
    quality = baseQuality
    img = PILImage.open(imgIn)
    for i in range(0, iterations):
        img = ImageEnhance.Contrast(img).enhance(2)
        img = ImageEnhance.Sharpness(img).enhance(2)
        img = ImageEnhance.Contrast(img).enhance(2)
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageEnhance.Contrast(img).enhance(2)
        img = img.filter(ImageFilter.EDGE_ENHANCE)
        img = ImageEnhance.Contrast(img).enhance(2)

        #img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        imgOut = BytesIO()
        img.save(imgOut, "JPEG", quality=quality)
        quality = int(quality*baseQuality/100)
        imgOut.seek(0)
        img = PILImage.open(imgOut)
    
    quality=baseQuality

    if scale < 1:
        ori = (img.width, img.height)
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    img = Tint(img, tintColor)
    img = ImageEnhance.Sharpness(img).enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.EDGE_ENHANCE)
    img = ImageEnhance.Sharpness(img).enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2)
    img = ImageOps.autocontrast(img)
    if scale < 1:
        img = img.resize(ori, PILImage.NEAREST)
    imgOut = BytesIO()
    img.save(imgOut, "JPEG", quality = quality)
    imgOut.seek(0)
    img = PILImage.open(imgOut)
    for i in range(0, secondIter):
        imgOut = BytesIO()
        img.save(imgOut, "JPEG", quality=quality)
        quality = int(quality*baseQuality/100)
        imgOut.seek(0)
        img = PILImage.open(imgOut)
        
    imgOut = BytesIO()
    img.save(imgOut, "JPEG", quality = quality)
    imgOut.seek(0)
    img = imgOut.read()
    img = Image(bytes=img)
    return CommandResult.Done(images=[img])

deepFryCmd = ImageCommand(
    'deepfry',
    DeepFry,
    desc='Deepfried memes.',
    images=['the image']
)
