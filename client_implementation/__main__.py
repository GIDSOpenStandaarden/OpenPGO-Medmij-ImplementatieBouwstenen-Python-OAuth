from os import (
    makedirs
)

from os.path import (
    dirname,
    join,
    exists
)

import base64
import logging

from argparse import ArgumentParser

from cryptography import (
    fernet
)

from aiohttp import (
    web
)

import jinja2
import aiohttp_jinja2

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event

from aiohttp_session import setup as setup_aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from medmij_oauth.client import (
    Client
)

from tests.util import (
    create_get_test_zal,
    create_get_test_gnl
)

from . util import (
    RequestMaker,
)

from . import (
    routes,
    SQLAlchemyDataStore,
    Base
)

from .middleware import setup_middleware

logging.basicConfig(level=logging.DEBUG)

request_maker = RequestMaker()

def setup_db(app, db_dir):
    db_session = sessionmaker(autoflush=False)

    if not exists(db_dir):
        makedirs(db_dir)
    db_path = join(db_dir, 'oauth_client.db')

    engine = create_engine('sqlite:///%s' % db_path, echo=False)

    db_session.configure(bind=engine)

    Base.metadata.bind = engine
    Base.metadata.create_all()

    app['db'] = engine
    app['db-session'] = db_session

def setup_routes(app):
    routes.setup_routes(app)

def setup_client(app, client_info):
    client = Client(
        data_store=SQLAlchemyDataStore(),
        client_info=client_info,
        make_request=request_maker.make_request,
        get_zal=create_get_test_zal(),
        get_gnl=create_get_test_gnl()
    )

    app['client'] = client

def setup_jinja2(app):
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(
            join(
                dirname(__file__),
                'templates'
            )
        )
    )

def setup_session(app):
    fernet_key = fernet.Fernet.generate_key()
    token = base64.urlsafe_b64decode(fernet_key)

    setup_aiohttp_session(app, EncryptedCookieStorage(token))

def main():
    parser = ArgumentParser(
        description='oauth client implementation'
    )

    parser.add_argument('--db-path', default='/db', type=str)
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--client_id', default='oauthclient.local', type=str)
    parser.add_argument('--base_url', default='https://oauthclient.local', type=str)

    args = parser.parse_args()

    app = web.Application()
    setup_db(app, args.db_path)
    setup_routes(app)

    setup_client(app, {
            'client_id': args.client_id,
            'redirect_uri': args.base_url + '/oauth/cb'
    })

    setup_jinja2(app)
    setup_session(app)
    setup_middleware(app)
    app.on_cleanup.append(request_maker.cleanup)
    web.run_app(app, port=args.port)

if __name__ == '__main__':
    main()
