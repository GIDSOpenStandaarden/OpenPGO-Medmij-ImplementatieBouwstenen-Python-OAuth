"""Server module for all OAuth related stuff"""
import urllib.parse
from . import (
    DataStore,
    tokens,
    validation
)

from medmij_oauth.exceptions import (
    OAuthException,
    ERRORS
)

class Server():
    """Server class for all OAuth related stuff"""
    @property
    def ocl(self):
        return self._get_ocl()

    def __init__(self, data_store=None, is_known_zg=None, zg_resource_available=None, get_ocl=None):
        assert is_known_zg is not None, "Can't instantiate Server without 'is_known_zg'"
        assert zg_resource_available is not None, "Can't instantiate Server without 'zg_resource_available'"
        assert get_ocl is not None, "Can't instantiate Server without 'get_ocl'"

        if not issubclass(data_store.__class__, DataStore):
            raise ValueError(
                'data_store argument should be a subclass of the DataStore abstract class'
            )

        self.data_store = data_store
        self._get_ocl = get_ocl
        self._is_known_zg = is_known_zg
        self._zg_resource_available = zg_resource_available

    def create_oauth_session(self, request_params, **kwargs):
        validation.validate_request_params(request_params, self.ocl)

        oauth_session = self.data_store.create_oauth_session(
            response_type=request_params.get('response_type'),
            client_id=request_params.get('client_id'),
            redirect_uri=request_params.get('redirect_uri'),
            scope=request_params.get('scope'),
            state=request_params.get('state'),
            **kwargs
        )

        return oauth_session

    def is_known_zg(self, oauth_session, **kwargs):
        if not self._is_known_zg(**kwargs):
            raise OAuthException(
                error_code=ERRORS.UNAUTHORIZED_CLIENT,
                error_description='Unknown ZG',
                base_redirect_url=oauth_session.redirect_uri,
                redirect=True
            )

    def zg_resource_available(self, oauth_session=None, oauth_session_id=None, client_data=None, **kwargs):
        if oauth_session is None:
            oauth_session = self.data_store.get_oauth_session_by_id(oauth_session_id)

        _client_data = {
            "bsn": oauth_session.client_bsn,
            **client_data
        }

        if not self._zg_resource_available(client_data=_client_data, **kwargs):
            raise OAuthException(
                error_code=ERRORS.ACCESS_DENIED,
                error_description='No such resource',
                base_redirect_url=oauth_session.redirect_uri,
                redirect=True
            )

        return True

    def handle_auth_grant(self, oauth_session_id=None, authorization=False, **kwargs):
        oauth_session = self.data_store.get_oauth_session_by_id(oauth_session_id, **kwargs)

        if oauth_session is None:
            raise ValueError('Not a valid oauth_session_id')

        if not authorization:
            self.data_store.update_oauth_session(oauth_session, {
                'authorization_granted': False
            }, **kwargs)

            oauth_session = self.data_store.save_oauth_session(oauth_session, **kwargs)

            raise OAuthException(
                error_code=ERRORS.ACCESS_DENIED,
                error_description='Authorization denied',
                base_redirect_url=oauth_session.redirect_uri,
                redirect=True
            )

        authorization_code = tokens.create_token()

        oauth_session = self.data_store.update_oauth_session(oauth_session, {
            'authorization_granted': True,
            'authorization_code': authorization_code.token,
            'authorization_code_expiration': authorization_code.expiration
        }, **kwargs)

        oauth_session = self.data_store.save_oauth_session(oauth_session, **kwargs)

        return (oauth_session, self.get_authorization_code_redirect_url(oauth_session, authorization_code))

    def get_authorization_code_redirect_url(self, oauth_session, authorization_code):
        query_dict = {
            'code': authorization_code.token,
            'state': oauth_session.state,
            'expires_in': authorization_code.lifetime.seconds,
            'token_type': 'bearer'
        }

        return f'{oauth_session.redirect_uri}?{urllib.parse.urlencode(query_dict)}'

    def redeem_authorization_code(self, request_params, **kwargs):
        oauth_session = self.data_store.get_oauth_session_by_authorization_code(
            request_params.get('code'),
            **kwargs
        )

        validation.validate_redeem_request(request_params, oauth_session)

        access_token = tokens.create_token()

        oauth_session = self.data_store.update_oauth_session(oauth_session, {
            'authorization_code': None,
            'access_token': access_token.token,
            'access_token_expiration': access_token.expiration
        }, **kwargs)

        oauth_session = self.data_store.save_oauth_session(oauth_session, **kwargs)

        return {
            'access_token': access_token.token,
            'token_type': 'bearer',
            'expires_in': access_token.lifetime.seconds,
            'scope': oauth_session.scope
        }

    def __repr__(self):
        return f'Server(data_store={repr(self.data_store)}, zg_resource_available={self._zg_resource_available.__name__})'