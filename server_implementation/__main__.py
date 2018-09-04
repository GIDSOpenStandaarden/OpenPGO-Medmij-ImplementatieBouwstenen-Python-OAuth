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

from medmij_oauth.server import (
    Server
)

from medmij_oauth.tests.util import (
    ret_false,
    ret_true,
    create_get_test_ocl
)

from . import (
    routes,
    SQLAlchemyDataStore,
    Base
)

from .middleware import setup_middleware

logging.basicConfig(level=logging.DEBUG)

def setup_db(app, db_dir):
    db_session = sessionmaker(autoflush=False)

    if not exists(db_dir):
        makedirs(db_dir)
    db_path = join(db_dir, 'oauth_server.db')

    engine = create_engine('sqlite:///%s' % db_path, echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    db_session.configure(bind=engine)

    Base.metadata.bind = engine
    Base.metadata.create_all()

    app['db'] = engine
    app['db-session'] = db_session

def setup_routes(app):
    routes.setup_routes(app)

def setup_server(app):
    server = Server(
        data_store=SQLAlchemyDataStore(),
        is_known_zg=ret_true,
        zg_resource_available=ret_true,
        get_ocl=create_get_test_ocl()
    )

    app['server'] = server

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
        description='oauth server implementation'
    )

    parser.add_argument('--db-path', default='/db', type=str)
    parser.add_argument('--port', default=8000, type=int)

    args = parser.parse_args()

    app = web.Application()
    setup_db(app, args.db_path)
    setup_routes(app)
    setup_server(app)
    setup_jinja2(app)
    setup_session(app)
    setup_middleware(app)
    web.run_app(app, port=args.port)

if __name__ == '__main__':
    main()
