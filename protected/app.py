import logging
import jose.jwt
import fastapi
import fastapi.middleware.cors
import starlette_oauth2_api


logger = logging.getLogger("protected")


class AuthenticateMiddleware(starlette_oauth2_api.AuthenticateMiddleware):
    """Override _provider_claims to allow JWT from any audience.

    Note that this means that only the issuer and the signature of the JWT
    are used for verification and the JWT is not tied to a specific application.

    See https://gitlab.com/jorgecarleitao/starlette-oauth2-api/-/blob/master/starlette_oauth2_api.py
    for the full source of the AuthenticationMiddleware class.
    """

    def _provider_claims(self, provider, token):
        """
        Validates the token and returns its respective claims against a specific provider.

        The ``at_hash`` value in the token, if present, is ignored, because in order to
        verify it, the access token would be required, which we don't have access to.

        The audience vlue is also ignored, since we are not concerned with which application
        the user authenticated with, just that the JWT was produced by the expected issuer.
        """
        issuer = self._providers[provider]["issuer"]
        audience = self._providers[provider]["audience"]
        logger.debug(
            'Trying to decode token for provider "%s", issuer "%s", audience "%s"...',
            provider,
            issuer,
            audience,
        )
        decoded = jose.jwt.decode(
            token,
            self._provider_keys(provider),
            issuer=issuer,
            audience=audience,
            options={"verify_at_hash": False, "verify_aud": False},  # Ignore at_hash, if present
        )
        logger.debug("Token decoded.")
        return decoded


app = fastapi.FastAPI()

"""Add the AuthenticationMiddleware to the application. The middleware is
called with every request, and if the request target is not in public_paths,
then the request is examined for q JWT in the form of a Authorization: Bearer
header. The JWT is validated using jose.jwt.decode. If invalid, then an exception
is thrown, otherwise the request continues with some request.scope['oauth2-claims'] 
set to contain the content of the decoded JWT. 
"""
app.add_middleware(AuthenticateMiddleware,
    providers={
        'orcid': {
            'keys': 'https://orcid.org/oauth/jwks',
            'issuer': 'https://orcid.org',
            'audience': 'foo',
        }
    },
    public_paths={'/'},
)


@app.get("/")
async def root():
    """Public endpoint is not protected by the AuthenticationMiddleware.
    """
    return {"message": "Public endpoint"}


@app.get("/protected")
async def root(request:fastapi.Request):
    """This method can only be accessed with a valid JWT issued by ORCID included in the
    Authorization: Bearer header..

    There are no restrictions on the user or the application that requested the JWT.
    """
    # The oauth2 properties are added to the request object by the authentication middleware
    # They can be used to determine the user etc.
    return {
        "message": "Protected endpoint",
        "provider": request.scope["oauth2-provider"],
        "claims": request.scope["oauth2-claims"],
    }
