import datetime
import uuid

from sqlalchemy import Column
from sqlalchemy.types import (
    DateTime,
    Text,
    Boolean
)

from . import Base

class OAuthSession(Base):
    """OAuthSession model"""
    __tablename__ = 'oauth_sessions'

    id = Column(Text, primary_key=True)
    response_type = Column(Text)
    client_id = Column(Text)
    scope = Column(Text)
    state = Column(Text)
    redirect_uri = Column(Text)
    created_at = Column(DateTime, nullable=False)
    relay_state = Column(Text, unique=True, nullable=True)
    authorization_code = Column(Text, unique=True, nullable=True)
    authorization_code_expiration = Column(DateTime, nullable=False)
    authorization = Boolean()
    access_token = Column(Text, unique=True)
    access_token_expiration = Column(DateTime, nullable=False)
    client_bsn = Column(Text)

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
        self.authorization_code_expiration = datetime.datetime.now()
        self.authorization = False
        self.access_token = None
        self.access_token_expiration = datetime.datetime.now()
