**Work in progress......**

# MedMij OAuth Lib

This repository contains a library to assist building a OAuth client/server implementation according to the MedMij specifications. Complementary to the library it also contains an example implementation of both client and server.

## Components

The library contains submodules i.e. Client, Server and Exceptions.

### Client

#### Methods:

``` __init__(data_store=None, get_zal=None, client_info=None, make_request=None):```

``` async get_zal() ```

``` async create_oauth_session(za_name, \*\*kwargs):```


``` async create_auth_request_url(oauth_session):```



``` async handle_auth_response(params, \*\*kwargs):```



``` async exchange_authorization_code(oauth_session, \*\*kwargs):```



### Server

#### Methods:


```def __init__(data_store=None, is_known_zg=None, zg_resource_available=None, get_ocl=None):```

```async def get_ocl()```

```async def create_oauth_session(request_params, **kwargs):```


```async def is_known_zg(oauth_session, **kwargs):```


```async def zg_resource_available(oauth_session=None, oauth_session_id=None, client_data=None, **kwargs):```


```async def handle_auth_grant(oauth_session_id=None, authorization=False, **kwargs):```


```def get_authorization_code_redirect_url(oauth_session, authorization_code):```

```async def exchange_authorization_code(request_params, **kwargs):```

### Exceptions

## Example implementations

### Client

### Server