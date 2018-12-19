from urllib.parse import urlparse

from medmij_oauth.exceptions import (
    OAuthException,
    lookup_error_code
)

def get_hostname(url):
    return urlparse(url).hostname

def validate_auth_response(data):
    if data.get("error"):
        return handle_error(data)

    if not data.get('code'):
        raise ValueError('Missing param \'code\' in auth response')

    if not data.get('state'):
        raise ValueError('Missing param \'state\' in auth response')

    return True

def validate_access_token_response(data, oauth_session):
    if oauth_session.access_token:
        raise ValueError('Access token already exchanged')

    if data.get("error"):
        return handle_error(data)

    if not data.get('access_token'):
        raise ValueError('No access token in response')

    if not data.get('token_type'):
        raise ValueError('No token_type present in response')

    return True

def handle_error(data):
    error = data.get('error')
    error_description = data.get('error_description')

    raise OAuthException(error_code=lookup_error_code(error), error_description=error_description)
