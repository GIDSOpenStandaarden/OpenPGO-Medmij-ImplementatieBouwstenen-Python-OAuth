from os import (
    open,
    path
)

import xml.etree.ElementTree as ET

from .zal import (
    parse_zal
)

def noop(*args, **kwargs):
    pass

def mock_make_request(url, data=None):
    pass