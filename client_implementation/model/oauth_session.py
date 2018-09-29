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
    state = Column(Text)
    scope = Column(Text)
    za_name = Column(Text)
    gegevensdienst_id = Column(Text)
    authorization_code = Column(Text)
    authorized = Column(Boolean)
    access_token = Column(Text)
    created_at = Column(DateTime, nullable=False)

    def __init__(self, state, za_name, gegevensdienst_id, scope):
        self.id = str(uuid.uuid4())
        self.state = state
        self.scope = scope
        self.za_name = za_name
        self.gegevensdienst_id = gegevensdienst_id
        self.authorization_code = None
        self.authorized = False
        self.access_token = None
        self.created_at = datetime.datetime.now()
