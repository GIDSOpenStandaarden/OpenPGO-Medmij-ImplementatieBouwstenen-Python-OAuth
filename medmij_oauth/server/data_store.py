import uuid
import datetime
from abc import ABC, abstractmethod

class DataStore(ABC):
    """Abstract Class for interactions with/manipulation of `OAuthSessions <#oauthsession>`__, subclass this class and implement it's methods"""
    @abstractmethod
    async def create_oauth_session(self, response_type, client_id, redirect_uri, scope, state, **kwargs):
        """Create a new oauth_session, persist the oauth_session and return it."""

    @abstractmethod
    async def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
        """Get a oauth_session based on its id and return it, else return None"""

    @abstractmethod
    async def get_oauth_session_by_authorization_code(self, authorization_code, **kwargs):
        """Get a oauth_session based on its authorization_code and return it, else return None"""

    @abstractmethod
    async def save_oauth_session(self, oauth_session, **kwargs):
        """Persist the current state of the oauth_session and return it"""

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
