# README for oauth_example

This is a minimal example of cross-application authentication using FastAPI and ORCID.

There are two web apps here: `authenticate` which authenticates a user and returns the generated JWT, and `protected` which has a protected endpoint that requires an ORCID JWT to access.

Although FastAPI is used as the web app here, the approach is not framework specific.

A brief description is provided below, more detailed explanations in the source.

See also:

* https://github.com/ORCID/ORCID-Source/blob/main/orcid-web/ORCID_AUTH_WITH_OPENID_CONNECT.md#authorization-code-flow
* https://info.orcid.org/documentation/integration-and-api-faq/
* https://gitlab.com/jorgecarleitao/starlette-oauth2-api/-/blob/master/starlette_oauth2_api.py
* https://docs.authlib.org/en/latest/client/starlette.html
* https://github.com/mpdavis/python-jose/blob/5ec9f48c1babcbfa62d433b29e55db8888c315ec/jose/jwt.py

## Install

Create a virtual environment, then install using poetry. For example:

```
git clone https://github.com/datadavev/oauth_example.git
cd oauth_example
python -m venv venv
source venv/bin/activate
poetry install
```

Or if you are using `direnv`:

```
git clone https://github.com/datadavev/oauth_example.git
cd oauth_example
direnv allow
poetry install
```

## authenticate

This app will authenticate via ORCID and present the resulting JWT.

To run the app, first visit ORCID, login, open the developer tools, and add an endpoint callback URL:

```
http://127.0.0.1:8000/oauthcallback
```

Make note of the Client ID and Client Secret for the next step.

Run the server like:

```
export ORCID_CLIENT_APP="Client ID"
export ORCID_CLIENT_SECRET="client secret"
fastapi dev --port 8000 authenticate/app.py
```

Vist `http://localhost:8000/auth` to log in via ORCID. The response page is JSON, the `id_token` property is the ORCID issued JWT value. 


## protected

This app has two end points: `/` which is publicly accessible and `/protected` which can only be accessed when the request includes a valid ORCID JWT.

Run the server like:

```
fastapi dev --port 8001 protected/app.py
```

Test access like:

```
EXPORT TOKEN="the value of id_token from the authenticate app (or any other ORCID JWT)"

curl -H "Authorization: Bearer ${TOKEN}" -s "http://localhost:8001/protected" | jq '.'
{
  "message": "Protected endpoint",
  "provider": "orcid",
  "claims": {
    "at_hash": "BVJZ...",
    "aud": "APP-ZTT8BDD9D2LPQNFV",
    "sub": "0000-0002-6513-4996",
    "auth_time": 1730729245,
    "iss": "https://orcid.org",
    "name": "Dave Vieglais",
    "exp": 1730815697,
    "given_name": "David",
    "iat": 1730729297,
    "nonce": "cb9H3CrUN97Iu9ADyXe6",
    "family_name": "Vieglais",
    "jti": "a741f264..."
  }
}
```
