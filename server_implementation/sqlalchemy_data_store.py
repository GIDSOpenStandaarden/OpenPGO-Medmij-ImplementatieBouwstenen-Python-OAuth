from medmij_oauth.server import DataStore
from .model import OAuthSession

class SQLAlchemyDataStore(DataStore):
    def create_oauth_session(self, response_type, client_id, redirect_uri, scope, state, **kwargs):
        db_session = kwargs.get('db')

        oauth_session = OAuthSession(
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state
        )

        db_session.add(oauth_session)
        db_session.commit()

        return oauth_session

    def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
        db_session = kwargs.get('db')

        oauth_session = db_session.query(OAuthSession).filter(
            OAuthSession.id == oauth_session_id
        ).first()

        return oauth_session

    def get_oauth_session_by_authorization_code(self, authorization_code, **kwargs):
        db_session = kwargs.get('db')

        oauth_session = db_session.query(OAuthSession).filter(
            OAuthSession.authorization_code == authorization_code
        ).first()

        return oauth_session

    def update_oauth_session(self, oauth_session, data, **kwargs):
        return super().update_oauth_session(oauth_session, data)

    def save_oauth_session(self, oauth_session, **kwargs):
        db_session = kwargs.get('db')

        db_session.commit()

        return oauth_session
