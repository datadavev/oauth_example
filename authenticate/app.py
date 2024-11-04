import os
import authlib.integrations.starlette_client
import fastapi
import fastapi.middleware.cors
import starlette.requests
import starlette.middleware.sessions


app = fastapi.FastAPI()


ORCID_CLIENT_SECRET=os.environ.get('ORCID_CLIENT_SECRET')
ORCID_CLIENT_ID=os.environ.get('ORCID_CLIENT_ID')


app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(starlette.middleware.sessions.SessionMiddleware, secret_key="some secret")

oauth = authlib.integrations.starlette_client.OAuth()

"""Registration here is using openid, which is a higher level wrapper
around the oauth end points. Take a look at the info at the
server_metadata_url
"""
oauth.register(
    name="orcid",
    client_id=ORCID_CLIENT_ID,
    client_secret=ORCID_CLIENT_SECRET,
    server_metadata_url="https://orcid.org/.well-known/openid-configuration",
    client_kwargs={"scope": "openid"},
    api_base_url="https://orcid.org",
)


@app.get("/")
async def root():
    return {"message": "Hello public. Visit /auth to login."}


@app.get("/auth")
async def auth(request: starlette.requests.Request):
    """Sends the user to ORCID for authentication and presents
    the resulting id_token.
    """
    redirect_url = "http://127.0.0.1:8000/oauthcallback"
    orcid = oauth.create_client('orcid')
    return await orcid.authorize_redirect(request, redirect_url)


@app.get("/oauthcallback")
async def oauthcallback(request: starlette.requests.Request):
    """
    This method is called back by ORCID oauth. It needs to be in the
    registered callbacks of the ORCID Oauth configuration.
    """
    orcid = oauth.create_client('orcid')
    token = await orcid.authorize_access_token(request)
    token_dict = dict(token)
    return {"id_token": token_dict}
