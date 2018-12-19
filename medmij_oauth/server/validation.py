import urllib.parse
import re

from datetime import (
    datetime
)

from medmij_oauth.exceptions import (
    ERRORS,
    OAuthException
)

def is_valid_hostname(hostname):
    if not hostname:
        return False

    if len(hostname) > 255:
        return False
    if hostname[-1] == '.':
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile('(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split('.'))

def validate_redirect_uri(url='', client_hostname=''):
    if not url:
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='redirect_uri required'
        )

    parsed_url = urllib.parse.urlsplit(url)

    if parsed_url[0] != 'https':
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='redirect_uri schema must be https'
        )

    if not is_valid_hostname(parsed_url[1]):
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='redirect_uri must be FQDN'
        )

    if parsed_url[3] != '':
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='redirect_uri can\'t contain query parameters'
        )

    if parsed_url[4] != '':
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='redirect_uri can\'t contain fragment'
        )

    if not client_hostname or not url.startswith('https://' + client_hostname):
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='redirect_uri must be in client domain'
        )
def is_expired(expiration_time=datetime.now()):
    return datetime.now() >= expiration_time

def validate_request_parameters(request_parameters, ocl):
    redirect_uri = request_parameters.get('redirect_uri', None)
    response_type = request_parameters.get('response_type', None)
    client_id = request_parameters.get('client_id', None)
    scope = request_parameters.get('scope', None)

    if not client_id:
        raise OAuthException(
            error_code=ERRORS.UNAUTHORIZED_CLIENT,
            error_description='client_id required'
        )

    if not ocl.get(client_id):
        raise OAuthException(
            error_code=ERRORS.INVALID_CLIENT,
            error_description='client unknown'
        )

    validate_redirect_uri(redirect_uri, ocl.get(client_id).hostname)

    if not response_type:
        raise OAuthException(
            error_code=ERRORS.UNSUPPORTED_RESPONSE_TYPE,
            error_description='response_type required',
            base_redirect_url=redirect_uri,
            redirect=True
        )

    if response_type != 'code':
        raise OAuthException(
            error_code=ERRORS.UNSUPPORTED_RESPONSE_TYPE,
            error_description='Only "code" response_type supported',
            base_redirect_url=redirect_uri,
            redirect=True
        )

    if not scope:
        raise OAuthException(
            error_code=ERRORS.INVALID_SCOPE,
            error_description='scope required',
            base_redirect_url=redirect_uri,
            redirect=True
        )

    # TODO implement match on scope (gegevensdienst_id) of current service
    try:
        if int(scope) >= 8:
            raise OAuthException(
                error_code=ERRORS.INVALID_SCOPE,
                error_description='Scope should be integer <= 8',
                base_redirect_url=redirect_uri,
                redirect=True
            )
    except Exception:
        raise OAuthException(
            error_code=ERRORS.INVALID_SCOPE,
            error_description='Scope should be integer <= 8',
            base_redirect_url=redirect_uri,
            redirect=True
        )

def validate_exchange_request(request_parameters, oauth_session):
    if oauth_session is None:
        raise OAuthException(
            error_code=ERRORS.INVALID_GRANT,
            error_description='Invalid authorization token'
        )

    grant_type = request_parameters.get('grant_type')
    client_id = request_parameters.get('client_id')
    redirect_uri = request_parameters.get('redirect_uri')

    if oauth_session.client_id != client_id or client_id is None:
        raise OAuthException(
            error_code=ERRORS.INVALID_CLIENT,
            error_description='client_id not associated with this authorization_token'
        )

    if redirect_uri is None:
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description=f'redirect_uri required'
        )

    if oauth_session.redirect_uri != redirect_uri:
        raise OAuthException(
            error_code=ERRORS.INVALID_REQUEST,
            error_description='Invalid redirect_uri'
        )

    if grant_type is None or grant_type != 'authorization_code':
        raise OAuthException(
            error_code=ERRORS.UNSUPPORTED_GRANT_TYPE,
            error_description='"authorization_code" in only supported grant_type'
        )

    if is_expired(oauth_session.authorization_code_expiration):
        raise OAuthException(
            error_code=ERRORS.INVALID_GRANT,
            error_description='Authorization token is expired'
        )
