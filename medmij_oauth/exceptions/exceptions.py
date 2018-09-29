'''
    Module for handling OAuth related errors
'''
import urllib.parse
import json

from enum import (
    Enum,
    auto
)

from http import HTTPStatus

class ERRORS(Enum):
    """
        Error codes enum to be used as error_code for instantiation of OAuthException

        Usage example:

        .. code:: python

            raise OAuthException(ERRORS.UNAUTHORIZED_CLIENT, 'no such resource', ...)
    """
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
    """
        Lookup error code by text.
        When an oauth client receives a error response, it can reproduce the exception by looking up the error code with the 'error' query param that it received.

        Raises a ValueError if the error passed to it is unknown.

        Example:

        .. code:: python

            error = query_params.get('error')
            error_description = query_params.get('error_description')

            raise OAuthException(error_code=lookup_error_code(error), error_description=error_description)

    """
    try:
        return [code for code, value in _ERRORS.items() if value['error'] == error][0]
    except IndexError:
        raise ValueError(f'Unknown error: \'{error}\'')

class OAuthException(BaseException):
    """
    OAuthException class, represents a oauth error as described in `rfc6749 <https://tools.ietf.org/html/rfc6749#section-4.1.1>`__

    :type error_code: :exc:`error code <medmij_oauth.exceptions.ERRORS>`
    :param error_code: Int that represents a type of error
    :type error_description: string
    :param error_description: Human readable description of the error e.g. 'no such resource'
    :type redirect: bool
    :param redirect: Indication if on handling of the exception the user should be redirected back to the client application of if the error should be rendered to the screen
    :type base_redirect_url: string (optional)
    :param base_redirect_url: The base of the redirect url (on redirection the error params are appended to the base_redirect_url as a query string)

    Usage examples:

    .. code:: python

        raise OAuthException(ERRORS.INVALID_REQUEST, error_description='Invalid redirect url', redirect=False)

    .. code:: python

        raise OAuthException(ERRORS.UNAUTHORIZED_CLIENT, error_description='No such resource', redirect=True, base_redirect_url='https://oauthclient.com')

    """
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
        """
            Return redirect url to which the end user should be redirected.
            The redirect_url constists of two parts, self.base_redirect_url and a query string that contains the error and error description

            Raises a Exception if self.direct != True or if self.base_redirect_url is not set.

            e.g.

            https://oauthclient.com/cb/?error=unauthorized_client&error_description=No%20such%20resource
        """
        if not self.redirect or not self.base_redirect_url:
            raise Exception('Not allowed to get redirect_url if redirect \
                is False or base_redirect_url is not set')

        error_query_string = urllib.parse.urlencode({
            'error': self.error,
            'error_description': self.error_description
        })

        return f'{self.base_redirect_url}?{error_query_string}'

    def get_json(self):
        """
        Return json representation of the exception that is targeted at the end user
        Included properties are 'error' and 'error_description'

        .. code:: python

            {
                'error': 'unauthorized_client',
                'error_description': 'no such resource'
            }
        """
        return json.dumps(self.get_dict())

    def get_dict(self):
        """
        Return dict representation of the exception that is targeted at the end user.
        Included properties are 'error' and 'error_description'.
        """
        return {
            'error': self.error,
            'error_description': self.error_description
        }

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'OAuthException(error_code={self.error_code}, error_description="{self.error_description}")'
