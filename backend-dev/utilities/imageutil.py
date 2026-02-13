from PIL import Image
import io
from typing import Tuple


def buffer_image(image: Image, format: str = 'JPEG'):
    # Store image in buffer, so we don't have to write it to disk.
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer, image


def resize(path: str, size: Tuple[int, int], format='JPEG', is_crop: bool = False):
    image = Image.open(path)
    if is_crop:
        image = crop_image_ratio_1(image)
    image = image.resize(size)
    return buffer_image(image, format)


def crop_image_ratio_1(image):
    width, height = image.size
    if width == height:
        return image
    offset = int(abs(height-width)/2)
    if width > height:
        image = image.crop([offset, 0, width-offset, height])
    else:
        image = image.crop([0, offset, width, height-offset])
    return image

def getResolution(path: str):
    im = Image.open(path)
    width, height = im.size
    
    return width, height