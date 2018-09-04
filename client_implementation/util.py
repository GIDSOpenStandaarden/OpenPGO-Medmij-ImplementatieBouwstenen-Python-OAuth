import ssl
import logging
import json
from os import path
import xml.etree.ElementTree as ET

import aiohttp

class RequestMaker():
    def __init__(self):
        self.sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=path.join(path.dirname(path.abspath(__file__)), 'trust/ca.crt')
        )

        conn = aiohttp.TCPConnector(ssl_context=self.sslcontext)

        self.session = aiohttp.ClientSession(connector=conn)

    async def cleanup(self, app):
        await self.session.close()

    async def make_request(self, method="POST", url='', body=None, params=None):
        optional_data = {}

        if body is not None:
            if not isinstance(body, str):
                body = json.dumps(body)

            optional_data['data'] = body.encode('utf-8')

        if params:
            optional_data['params'] = params

        async with self.session.request(method, url, **optional_data) as resp:
            logging.debug('making request: %s, %s, %s' % (method, url, optional_data['data']))

            json_resp = await resp.json()

        return json_resp