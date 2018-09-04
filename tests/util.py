from os import path
import xml.etree.ElementTree as ET

from medmij_oauth.server import parse_ocl
from medmij_oauth.client import parse_zal

def ret_false(**kwargs):
    return False

def ret_true(**kwargs):
    return True

def create_get_test_ocl():
    ocl = None
    def get_test_ocl():
        nonlocal ocl
        if ocl is not None:
            return ocl

        ocl = parse_ocl(ET.parse(
            path.join(path.dirname(__file__), 'resources/ocl.xml')
        ).getroot())

        return ocl

    return get_test_ocl

from medmij_oauth.client.zal import parse_zal

def create_get_test_zal():
    zal = None
    def get_test_zal():
        nonlocal zal
        if zal is not None:
            return zal

        zal = parse_zal(ET.parse(
            path.join(path.dirname(__file__), 'resources/zal.xml')
        ).getroot())

        return zal

    return get_test_zal

def create_mock_make_request(response):
    async def inner(**kwargs):
        return response

    return inner