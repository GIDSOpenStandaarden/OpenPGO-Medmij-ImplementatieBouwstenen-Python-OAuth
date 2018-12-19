from os import path
import xml.etree.ElementTree as ET

import medmij as medmij_lists
from medmij_oauth.client import parse_gnl

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

        with open(path.join(path.dirname(__file__), 'resources/ocl.xml'), 'r') as file:
            xml = bytes(file.read(), 'utf-8')

        return medmij_lists.OAuthclientList(xmldata=xml)

    return get_test_ocl

def create_get_test_gnl():
    gnl = None
    async def get_test_gnl():
        nonlocal gnl
        if gnl is not None:
            return gnl

        gnl = parse_gnl(ET.parse(
            path.join(path.dirname(__file__), 'resources/MedMij_Gegevensdienstnamenlijst_example.xml')
        ).getroot())

        return gnl
    
    return get_test_gnl

def create_get_test_zal():
    zal = None
    async def get_test_zal():
        nonlocal zal
        if zal is not None:
            return zal

        with open(path.join(path.dirname(__file__), 'resources/zal.xml'), 'r') as file:
            xml = bytes(file.read(), 'utf-8')

        zal = medmij_lists.ZAL(xmldata=xml)

        return zal

    return get_test_zal

def create_mock_make_request(response):
    async def inner(**kwargs):
        return response

    return inner