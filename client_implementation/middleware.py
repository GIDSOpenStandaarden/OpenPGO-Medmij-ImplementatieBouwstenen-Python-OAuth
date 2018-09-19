from aiohttp import web
from medmij_oauth.exceptions import OAuthException

def setup_middleware(app):
    app.middlewares.append(oauth_error_middleware)
    app.middlewares.append(require_db)

@web.middleware
async def oauth_error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except OAuthException as ex:
        # TODO Remove
        if ex.redirect:
            return web.HTTPFound(ex.get_redirect_url())

        return web.Response(
            text=ex.get_json(),
            status=ex.status_code,
            content_type='application/json'
        )

@web.middleware
async def require_db(request, handler):
    session = request.app['db-session']()
    try:
        request.db = session
        return await handler(request)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
