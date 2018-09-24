from os import path
import xml.etree.ElementTree as ET

from medmij_oauth.server import parse_ocl
from medmij_oauth.client import parse_gnl
from medmij_oauth.client import parse_zal

async def ret_false(**kwargs):
    return False

async def ret_true(**kwargs):
    return True

def create_get_test_ocl():
    ocl = None
    async def get_test_ocl():
        nonlocal ocl
        if ocl is not None:
            return ocl

        ocl = parse_ocl(ET.parse(
            path.join(path.dirname(__file__), 'resources/ocl.xml')
        ).getroot())

        return ocl

    return get_test_ocl

from medmij_oauth.client.zal import parse_zal

async def get_test_gnl():
    nonlocal gnl
    if gnl is not None:
        return gnl

    gnl = parse_gnl(ET.parse(
        path.join(path.dirname(__file__), 'resources/MedMij_Gegevensdienstnamenlijst_example.xml')
    ).getroot())

    return gnl

def create_get_test_zal():
    zal = None
    async def get_test_zal():
        nonlocal zal
        if zal is not None:
            return zal
        gnl = await get_test_zal()

        zal = parse_zal(ET.parse(
            path.join(path.dirname(__file__), 'resources/zal.xml')
        ).getroot(), gnl)

        return zal

    return get_test_zal

def create_mock_make_request(response):
    async def inner(**kwargs):
        return response

    return inner