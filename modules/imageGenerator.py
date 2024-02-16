from PIL import Image
import requests


images_path = "./images/res"

async def generateImage(url: str):
    im1 = Image.open(requests.get(url, stream=True).raw)
    imagen2 = Image.open(f'{images_path}/basura2.png')
    
    im = Image.new('RGBA', im1.size, (0, 0, 0, 0))
    
    im2 = imagen2.resize(im1.size)
    
    im.paste(im1)
    im.paste(im2, (0,0), im2)
    im.save(f'{images_path}/basura.png')
    return f'{images_path}/basura.png'
    
