import logging
from os import urandom
from binascii import hexlify

from aiohttp import web
from aiohttp_session import get_session

async def generate_csrf_token(request):
    session = await get_session(request)
    if 'csrf_token' not in session:
        token = hexlify(urandom(64)).decode('utf8')
        session['csrf_token'] = token

    return session['csrf_token']

def require_csrf(fn):
    async def wrap(*args, **kwargs):
        request = args[0]
        session = await get_session(request)

        if request.method == 'POST':
            post = await request.post()

            if 'csrf_token' not in session:
                logging.debug('[require_csrf]: No csrf token ready')
                return web.Response(status=500,
                                    text='Internal error: No CSRF token ready')

            if 'csrf_token' not in post:
                logging.warning('[require_csrf]: No CSRF token presented')
                return web.Response(status=403,
                                    text='Error: Invalid CSRF token')


            if post['csrf_token'] != session['csrf_token']:
                logging.warning('[require_csrf]: Invalid CSRF token')
                return web.Response(status=403,
                                    text='Error: Invalid CSRF token')

        return await fn(*args, **kwargs)

    return wrap
