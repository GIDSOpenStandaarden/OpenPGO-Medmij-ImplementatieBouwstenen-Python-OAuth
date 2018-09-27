from aiohttp import web
from aiohttp_jinja2 import render_template

from . import csrf

async def get_start_oauth_session(request):
    query_dict = request.query
    server = request.app['server']

    oauth_session = await server.create_oauth_session(query_dict, db=request.db)

    # If there is no resource available the function raises an OAuthException that gets handled by the middleware
    await server.zg_resource_available(oauth_session=oauth_session, client_data={"name": "test patient"})

    ocl = await server.get_ocl()
    pgo = ocl.get(oauth_session.client_id)

    csrf_token = await csrf.generate_csrf_token(request)

    return render_template('ask_auth.html', request, {
        'pgo': pgo,
        'oauth_session_id': oauth_session.id,
        'csrf_token': csrf_token
    })

@csrf.require_csrf
async def post_grant_auth(request):
    post = await request.post()
    server = request.app['server']

    _, redirect_url = await server.handle_auth_grant(
        request.match_info.get('oauth_session_id'),
        post.get('auth_granted', False) == 'true',
        db=request.db
    )

    return web.HTTPFound(redirect_url)

async def post_exchange_authorization_code(request):
    # POST /oauth/token HTTP/1.1
    # Host: authorization-server.com
    #
    # grant_type=authorization_code
    # &code=xxxxxxxxxxx
    # &redirect_uri=https://example-app.com/redirect
    # &client_id=xxxxxxxxxx
    # &client_secret=xxxxxxxxxx

    payload = await request.json()
    access_token = await request.app['server'].exchange_authorization_code(payload, db=request.db)

    return web.json_response(access_token)
