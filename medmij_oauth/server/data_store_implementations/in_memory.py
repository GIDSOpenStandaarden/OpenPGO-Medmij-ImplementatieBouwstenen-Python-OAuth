import uuid
import datetime

from ..data_store import (
    DataStore
)

SESSIONS = {}

class InMemoryDataStore(DataStore):
    async def create_oauth_session(self, response_type, client_id, redirect_uri, scope, state, **kwargs):
        oauth_session = OAuthSession(
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state
        )

        SESSIONS[oauth_session.id] = oauth_session

        return oauth_session

    async def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
        return SESSIONS.get(oauth_session_id, None)

    async def get_oauth_session_by_authorization_code(self, authorization_code, **kwargs):
        try:
            oauth_session = [
                oauth_session for
                oauth_session in SESSIONS.values()
                if oauth_session.authorization_code == authorization_code
            ][0]
        except IndexError:
            return None

        return oauth_session

    async def save_oauth_session(self, oauth_session=None, **kwargs):
        return oauth_session

    def __repr__(self):
        return 'InMemoryDataStore()'

class OAuthSession():
    def __init__(self, response_type, client_id, redirect_uri, scope, state):
        self.id = str(uuid.uuid4())
        self.response_type = response_type
        self.client_id = client_id
        self.scope = scope
        self.state = state
        self.redirect_uri = redirect_uri
        self.created_at = datetime.datetime.now()
        self.authorization_code = None
        self.authorization_code_expiration = -1
        self.authorization_granted = False
        self.access_token = None
        self.access_token_expiration = -1
        self.zorggebruiker_bsn = ''
