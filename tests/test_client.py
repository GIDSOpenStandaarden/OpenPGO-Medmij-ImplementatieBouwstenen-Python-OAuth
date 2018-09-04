from pytest import (
    fixture,
    raises,
    mark
)
from medmij_oauth.client import (
    Client,
    InMemoryDataStore
)

from medmij_oauth.exceptions import OAuthException

from .util import (
    ret_true,
    ret_false,
    create_get_test_zal,
    create_mock_make_request
)

@fixture
def client(request):
    return Client(
        data_store=InMemoryDataStore(),
        client_info={
            'client_id': 'oauthclient.local',
            'redirect_uri': 'https://oauthclient.local/oauth/cb'
        },
        get_zal=create_get_test_zal(),
        make_request=create_mock_make_request({})
    )

@fixture
def oauth_session(client):
    za = client.zal['oauthserver.local@medmij']

    return client.create_oauth_session(za.naam)

def test_create_oauth_session(client):
    za = client.zal['oauthserver.local@medmij']

    oauth_session = client.create_oauth_session(za.naam)

    assert oauth_session.za_name == za.naam

def test_create_auth_request_url(client, oauth_session):
    # python 3.6 has ordered dict keys so seralization of session is predictable
    # {
    #     'state': oauth_session.state,
    #     'scope': 1,
    #     'response_type': 'code',
    #     'client_id': self.client_info['client_id'],
    #     'redirect_url': self.client_info['redirect_uri']
    # }

    req_url = f'https://oauthserver.local/oauth/authorize?state={oauth_session.state}&scope=1&response_type=code&client_id=oauthclient.local&redirect_uri=https%3A%2F%2Foauthclient.local%2Foauth%2Fcb'

    assert client.create_auth_request_url(oauth_session) == req_url

def test_handle_auth_response_valid(client, oauth_session):
    response = {
        'code': 'SplxlOBeZQQYbYS6WxSbIA',
        'state': oauth_session.state
    }

    _oauth_session = client.handle_auth_response(response)

    assert _oauth_session
    assert _oauth_session.authorization_code == response['code']
    assert _oauth_session.authorized

def test_handle_auth_response_invalid(client, oauth_session):
    # code not in response
    response = {
        'code': '',
        'state': '-'
    }

    with raises(ValueError) as ex_info:
        client.handle_auth_response(response)

    assert "Missing param 'code' in auth response" in str(ex_info.value)

    # state not in response
    response = {
        'code': 'SplxlOBeZQQYbYS6WxSbIA',
        'state': ''
    }

    with raises(ValueError) as ex_info:
        client.handle_auth_response(response)

    assert "Missing param 'state' in auth response" in str(ex_info.value)

    # state in response not linked to oauth_session
    response = {
        'code': 'SplxlOBeZQQYbYS6WxSbIA',
        'state': '-'
    }

    with raises(ValueError) as ex_info:
        client.handle_auth_response(response)

    assert 'No oauth_session found!' in str(ex_info.value)

    # response is known oauth error response
    response = {
        'error': 'access_denied',
        'error_description': 'No such resource'
    }

    with  raises(OAuthException) as ex_info:
        client.handle_auth_response(response)

    assert ex_info.value.error == 'access_denied'
    assert ex_info.value.error_description == 'No such resource'

    # response contains unknown error
    response = {
        'error': 'random_string',
        'error_description': 'Lala'
    }

    with  raises(ValueError) as ex_info:
        client.handle_auth_response(response)

    err = f'Unknown error: \'random_string\''

    assert err in str(ex_info.value)

@mark.asyncio
async def test_redeem_authorization_code_valid(client, oauth_session):
    response = {
        'code': 'SplxlOBeZQQYbYS6WxSbIA',
        'state': oauth_session.state
    }

    oauth_session = client.handle_auth_response(response)

    client.make_request = create_mock_make_request({
        'access_token': 'abcd1234',
        'token_type': 'bearer'
    })

    oauth_session = await client.redeem_authorization_code(oauth_session)

    assert oauth_session.access_token == 'abcd1234'

@mark.asyncio
async def test_redeem_authorization_code_invalid(client, oauth_session):
    response = {
        'code': 'SplxlOBeZQQYbYS6WxSbIA',
        'state': oauth_session.state
    }

    oauth_session = client.handle_auth_response(response)

    client.make_request = create_mock_make_request({
        'access_token': '',
        'token_type': 'bearer'
    })

    with raises(ValueError) as ex_info:
        oauth_session = await client.redeem_authorization_code(oauth_session)

    assert 'No access token in response' in str(ex_info.value)

    client.make_request = create_mock_make_request({
        'access_token': 'abcd1234',
        'token_type': ''
    })

    with raises(ValueError) as ex_info:
        oauth_session = await client.redeem_authorization_code(oauth_session)

    assert 'No token_type present in response' in str(ex_info.value)

    assert not oauth_session.access_token