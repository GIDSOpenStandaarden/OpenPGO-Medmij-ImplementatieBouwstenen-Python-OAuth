'''
    Module for handling OAuth related _ERRORS

    references:
    https://www.oauth.com/oauth2-servers/authorization/the-authorization-response/
    https://tools.ietf.org/html/rfc6749#section-5.2
'''
import urllib.parse
import json

from enum import (
    Enum,
    auto
)

from http import HTTPStatus

class ERRORS(Enum):
    INVALID_REQUEST = auto()
    ACCESS_DENIED = auto()
    UNAUTHORIZED_CLIENT = auto()
    UNSUPPORTED_RESPONSE_TYPE = auto()
    INVALID_SCOPE = auto()
    SERVER_ERROR = auto()
    TEMPORARILY_UNAVAILABLE = auto()
    INVALID_CLIENT = auto()
    INVALID_GRANT = auto()
    UNSUPPORTED_GRANT_TYPE = auto()

_ERRORS = {
    ERRORS.INVALID_REQUEST: {
        "error": "invalid_request",
        "status_code": HTTPStatus.BAD_REQUEST
    },
    ERRORS.ACCESS_DENIED: {
        "error": "access_denied",
        "status_code": HTTPStatus.BAD_REQUEST
    },
    ERRORS.UNAUTHORIZED_CLIENT: {
        "error": "unauthorized_client",
        "status_code": HTTPStatus.UNAUTHORIZED
    },
    ERRORS.UNSUPPORTED_RESPONSE_TYPE: {
        "error": "unsupported_response_type",
        "status_code": HTTPStatus.BAD_REQUEST
    },
    ERRORS.INVALID_SCOPE: {
        "error": "invalid_scope",
        "status_code": HTTPStatus.BAD_REQUEST
    },
    ERRORS.SERVER_ERROR: {
        "error": "server_error",
        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR
    },
    ERRORS.TEMPORARILY_UNAVAILABLE: {
        "error": "temporarily_unavailable",
        "status_code": HTTPStatus.SERVICE_UNAVAILABLE
    },
    ERRORS.INVALID_CLIENT: {
        "error": "invalid_client",
        "status_code": HTTPStatus.BAD_REQUEST
    },
    ERRORS.INVALID_GRANT: {
        "error": "invalid_grant",
        "status_code": HTTPStatus.BAD_REQUEST
    },
    ERRORS.UNSUPPORTED_GRANT_TYPE: {
        "error": "unsupported_grant_type",
        "status_code": HTTPStatus.BAD_REQUEST
    }
}

def lookup_error_code(error):
    try:
        return [code for code, value in _ERRORS.items() if value['error'] == error][0]
    except IndexError:
        raise ValueError(f'Unknown error: \'{error}\'')

class OAuthException(BaseException):
    def __init__(
            self,
            error_code,
            error_description='',
            redirect=False,
            base_redirect_url=''
        ):
        error = _ERRORS[error_code]
        super(OAuthException, self).__init__(error_description)

        self.error_code = error_code
        self.error_description = error_description
        self.status_code = error["status_code"]
        self.error = error["error"]
        self.redirect = redirect
        self.base_redirect_url = base_redirect_url

    def get_redirect_url(self):
        if not self.redirect or not self.base_redirect_url:
            raise Exception('Not allowed to get redirect_url if redirect \
                is False or base_redirect_url is not set')

        error_query_string = urllib.parse.urlencode({
            'error': self.error,
            'error_description': self.error_description
        })

        return f'{self.base_redirect_url}?{error_query_string}'

    def get_json(self):
        return json.dumps(self.get_dict())

    def get_dict(self):
        return {
            'error': self.error,
            'error_description': self.error_description
        }

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'OAuthException(error_code={self.error_code}, error_description="{self.error_description}")'