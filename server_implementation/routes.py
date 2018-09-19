from .views import (
    get_start_oauth_session,
    post_grant_auth,
    post_exchange_authorization_code
)

def setup_routes(app):
    app.router.add_get('/oauth/authorize', get_start_oauth_session)
    app.router.add_post('/oauth/grant_auth/{oauth_session_id}', post_grant_auth)
    app.router.add_post('/oauth/token', post_exchange_authorization_code)
