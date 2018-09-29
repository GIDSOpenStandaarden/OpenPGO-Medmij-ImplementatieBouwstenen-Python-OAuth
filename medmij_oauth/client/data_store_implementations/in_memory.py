import secrets
import uuid

from ..data_store import (
    DataStore
)

SESSIONS = {}

class InMemoryDataStore(DataStore):
    async def create_oauth_session(self, za_name, gegevensdienst_id, **kwargs):
        oauth_session = OAuthSession(
            state=secrets.token_hex(16),
            za_name=za_name,
            gegevensdienst_id=gegevensdienst_id,
            scope=gegevensdienst_id
        )

        SESSIONS[oauth_session.id] = oauth_session

        return oauth_session

    async def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
        return SESSIONS.get(oauth_session_id, None)

    async def get_oauth_session_by_state(self, state, **kwargs):
        try:
            oauth_session = [
                oauth_session for
                oauth_session in SESSIONS.values()
                if oauth_session.state == state
            ][0]
        except IndexError:
            return None

        return oauth_session

    async def save_oauth_session(self, oauth_session=None, **kwargs):
        return oauth_session

    def __repr__(self):
        return 'InMemoryDataStore()'

class OAuthSession():
    def __init__(self, state, za_name, gegevensdienst_id, scope):
        self.id = str(uuid.uuid4())
        self.state = state
        self.scope = scope
        self.za_name = za_name
        self.gegevensdienst_id = gegevensdienst_id
        self.authorization_code = None
        self.authorized = False
        self.access_token = None
