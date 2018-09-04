import urllib.parse

from . import validation

from .data_store import DataStore

class Client:
    @property
    def zal(self):
        return self._get_zal()

    def __init__(self, data_store=None, get_zal=None, client_info=None, make_request=None):
        assert get_zal is not None, "Can't instantiate Client without 'get_zal'"
        assert make_request is not None, "Can't instantiate Client without 'make_request'"
        assert client_info, "Can't instantiate Client without 'client_info'"

        if not issubclass(data_store.__class__, DataStore):
            raise ValueError(
                'data_store argument should be a subclass of the DataStore abstract class'
            )

        self.data_store = data_store
        self.client_info = client_info
        self.make_request = make_request
        self._get_zal = get_zal

    def create_oauth_session(self, za_name, **kwargs):
        return self.data_store.create_oauth_session(za_name=za_name, **kwargs)

    def create_auth_request_url(self, oauth_session):
        request_dict = {
            'state': oauth_session.state,
            'scope': 1,
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }

        za = self.zal[oauth_session.za_name]
        query_params = urllib.parse.urlencode(request_dict)

        return f'{za.authorization_endpoint}?{query_params}'

    def handle_auth_response(self, params, **kwargs):
        validation.validate_auth_response(params)

        oauth_session = self.data_store.get_oauth_session_by_state(params['state'], **kwargs)

        if oauth_session is None:
            raise ValueError('No oauth_session found!')

        oauth_session = self.data_store.update_oauth_session(oauth_session, {
            'authorization_code': params['code'],
            'authorized': True
        }, **kwargs)

        oauth_session = self.data_store.save_oauth_session(oauth_session, **kwargs)

        return oauth_session

    async def redeem_authorization_code(self, oauth_session, **kwargs):
        za = self.zal[oauth_session.za_name]

        response = await self.make_request(method='POST', url=za.token_endpoint, body={
            'grant_type': 'authorization_code',
            'code': oauth_session.authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id
        })

        validation.validate_access_token_response(response, oauth_session)

        oauth_session = self.data_store.update_oauth_session(oauth_session, {
            'access_token': response['access_token'],
            'authorization_code': None
        }, **kwargs)

        oauth_session = self.data_store.save_oauth_session(oauth_session, **kwargs)

        return oauth_session

    def __repr__(self):
        return f'Client(data_store={repr(self.data_store)}, get_zal={self._get_zal.__name__})'

    def __getattr__(self, attr):
        try:
            return self.client_info[attr]
        except AttributeError:
            pass

        raise AttributeError(f'Client has no attribute \'{attr}\'')
