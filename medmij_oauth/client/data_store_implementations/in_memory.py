import secrets
from ..data_store import (
    DataStore,
    OAuthSession
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
