from line2.models.command import ImageCommand, Parameter, ParameterType, CommandResult, CommandResultType
from random import random
from line2.utils import IsEmpty
from io import BytesIO
from line2.models.content import Image
from PIL import Image as PILImage

def JPEG(message, options, images=[], quality=50, iterations=50):
    img = images[0].bytes
    imgIn = BytesIO(img)
    baseQuality=quality
    for i in range(0, iterations):
        #open previously generated file
        compImg = PILImage.open(imgIn)
        #compress file at 50% of previous quality
        imgOut = BytesIO()
        compImg.save(imgOut, "JPEG", quality=quality)
        quality = int(quality*baseQuality/100)
        imgIn = imgOut
        imgIn.seek(0)
    img = imgIn.read()
    img = Image(bytes=img)
    return CommandResult.Done(images=[img])

jpegCmd = ImageCommand(
    'jpeg',
    JPEG,
    desc='Adds JPEG artifacts',
    images=['the image']
)
