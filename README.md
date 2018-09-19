**Work in progress**

# MedMij OAuth Lib

This repository contains a library to assist building a OAuth client/server implementation according to the MedMij specifications. Complementary to the library it also contains an example implementation of both client and server.

## Components

The library contains submodules i.e. Client, Server and Exceptions.

### Client

#### properties:
*zal*

#### methods:

**__init__(data_store=None, get_zal=None, client_info=None, make_request=None):**

**async create_oauth_session(za_name, \*\*kwargs):**


**async create_auth_request_url(oauth_session):**


**async handle_auth_response(params, \*\*kwargs):**


**async exchange_authorization_code(oauth_session, \*\*kwargs):**


### Server

### Exceptions

## Example implementations

### Client

### Server