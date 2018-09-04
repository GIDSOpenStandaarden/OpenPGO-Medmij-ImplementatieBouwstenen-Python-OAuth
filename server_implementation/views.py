from aiohttp import web
from aiohttp_jinja2 import render_template

from . import csrf

async def get_start_oauth_session(request):
    query_dict = request.query
    server = request.app['server']

    oauth_session = server.create_oauth_session(query_dict, db=request.db)

    server.is_known_zg(oauth_session=oauth_session)
    server.zg_resource_available(oauth_session=oauth_session)

    pgo = server.ocl.get(oauth_session.client_id)

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

    _, redirect_url = server.handle_auth_grant(
        request.match_info.get('oauth_session_id'),
        post.get('auth_granted', False) == 'true',
        db=request.db
    )

    return web.HTTPFound(redirect_url)

async def post_redeem_authorization_code(request):
    # POST /oauth/token HTTP/1.1
    # Host: authorization-server.com
    #
    # grant_type=authorization_code
    # &code=xxxxxxxxxxx
    # &redirect_uri=https://example-app.com/redirect
    # &client_id=xxxxxxxxxx
    # &client_secret=xxxxxxxxxx

    payload = await request.json()
    access_token = request.app['server'].redeem_authorization_code(payload, db=request.db)

    return web.json_response(access_token)
