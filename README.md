# README for oatuh_example

This is a minimal example of cross-application authentication using FastAPI and ORCID.

There are two web apps here: `authenticate` and `protected`.

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
