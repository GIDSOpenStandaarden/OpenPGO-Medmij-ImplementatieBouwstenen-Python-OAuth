from aiohttp import web
from aiohttp_jinja2 import render_template

from . import csrf

from medmij_oauth.exceptions import OAuthException

async def get_select_zal(request):
    client = request.app['client']

    csrf_token = await csrf.generate_csrf_token(request)

    return render_template('select_zal.html', request, {
        'zal': await client.get_zal(),
        'csrf_token': csrf_token
    })

@csrf.require_csrf
async def post_select_zal(request):
    post = await request.post()
    client = request.app['client']

    oauth_session = await client.create_oauth_session(za_name=post.get('za'), db=request.db)

    url = await client.create_auth_request_url(oauth_session)

    return web.HTTPFound(url)

async def get_cb(request):
    query = request.query
    client = request.app.get('client')

    try:
        oauth_session = await client.handle_auth_response(query, db=request.db)
    except OAuthException as ex:
        return render_template('error.html', request, {'error': ex})

    try:
        oauth_session = await client.exchange_authorization_code(oauth_session, db=request.db)
    except OAuthException as ex:
        return  web.HTTPFound('/oauth/error?error=' + ex.error) #render_template('error.html', request, {'error': ex})

    return  web.HTTPFound('/oauth/success') #render_template('success.html', request, {})

async def get_error(request):
    return render_template('error.html', request, {'error': request.query})

async def get_success(request):
    return render_template('success.html', request, {})
