import uuid
from abc import ABC, abstractmethod

class DataStore(ABC):
    """Abstract Class for data access, subclass this class and implement it's methods"""
    @abstractmethod
    async def create_oauth_session(self, state, za_name, gegevensdienst_id, **kwargs):
        """Create a new oauth_session, persist the oauth_session and return it."""

    @abstractmethod
    async def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
        """Get a oauth_session based on it's id and return it, else return None"""

    @abstractmethod
    async def get_oauth_session_by_state(self, state, **kwargs):
        """Get a oauth_session based on the state param and return it, else return None"""

    @abstractmethod
    async def save_oauth_session(self, oauth_session, **kwargs):
        """Persist the current state of the oauth_session and return it"""

class OAuthSession():
    def __init__(self, state, za_name, gegevensdienst_id, scope):
        self.id = str(uuid.uuid4())
        self.state = state
        self.scope = gegevensdienst_id
        self.za_name = za_name
        self.gegevensdienst_id = gegevensdienst_id
        self.authorization_code = None
        self.authorized = False
        self.access_token = None
