from pyzbar.pyzbar import decode
from PIL import Image
import openfoodfacts


def readcode(file):
    codes=decode(Image.open('./static/img_db/'+file))
    return codes[0].data.decode("utf-8")


def getInfos(code) :
    product = openfoodfacts.products.get_product('3561452828692')
    if product['product']['status_verbose']=='product found' :
        try :
            img=product['product']['image_small_url']
        except :

            pass
        try :
            nutriscore=product['product']['nutriscore_grade']
        except:
            pass
        url='https://world.openfoodfacts.org/product/'+code;