import uuid
import datetime
from abc import ABC, abstractmethod

class DataStore(ABC):
    """Abstract Class for data access, subclass this class and implement it's methods"""
    @abstractmethod
    def create_oauth_session(self, response_type, client_id, redirect_uri, scope, state, **kwargs):
        """Create a new oauth_session, persist the oauth_session and return it."""

    @abstractmethod
    def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
        """Get a oauth_session based on it's id and return it, else return None"""

    @abstractmethod
    def get_oauth_session_by_authorization_code(self, authorization_code, **kwargs):
        """Get a oauth_session based on it's authorization_code and return it, else return None"""

    @abstractmethod
    def update_oauth_session(self, oauth_session, data, **kwargs):
        """
        Update the oauth_session with de keys and values contained
        in the data dict and return the updated oauth_session
        """
        for key, value in data.items():
            try:
                getattr(oauth_session, key)
            except AttributeError:
                continue

            setattr(oauth_session, key, value)

        return oauth_session

    @abstractmethod
    def save_oauth_session(self, oauth_session, **kwargs):
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
        self.relay_state = str(uuid.uuid4())
        self.authorization_code = None
        self.authorization_code_expiration = -1
        self.authorization_granted = False
        self.access_token = None
        self.access_token_expiration = -1
        self.client_bsn = ''
