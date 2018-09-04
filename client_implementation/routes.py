from .views import (
    get_select_zal,
    post_select_zal,
    get_cb,
    get_error,
    get_success
)

def setup_routes(app):
    app.router.add_get('/oauth/start', get_select_zal)
    app.router.add_post('/oauth/start', post_select_zal)
    app.router.add_get('/oauth/cb', get_cb)
    app.router.add_get('/oauth/error', get_error)
    app.router.add_get('/oauth/success', get_success)
