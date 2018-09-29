from abc import ABC, abstractmethod

class DataStore(ABC):
    """Abstract Class that handles interaction instantiation, persisting and lookups of OAuthSessions."""
    @abstractmethod
    async def create_oauth_session(self, state, za_name, gegevensdienst_id, scope, **kwargs):
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
