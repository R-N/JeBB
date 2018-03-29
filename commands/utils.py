from PIL import ImageChops, Image as PILImage
from http.client import HTTPConnection
from time import sleep
from traceback import format_stack, print_exc


def Tint(image, color):
    return ImageChops.blend(image, PILImage.new('RGB', image.size, color), 0.36)

def GetStatusCode(host, path="/"):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        conn = HTTPConnection(host)
        conn.request("HEAD", path)
        return conn.getresponse().status
    except Exception:
        return None
    
def WaitOK(host, path="/"):
    while GetStatusCode(host, path) != 200:
        sleep(5)
        