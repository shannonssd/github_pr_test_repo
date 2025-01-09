from authlib.integrations.django_oauth2 import ResourceProtector  # type: ignore
from django.conf import settings

from . import validator


class MockedResourceProtector(ResourceProtector):
    def acquire_token(self, request, scopes=None):
        if settings.ENABLE_AUTH0_AUTHENTICATION:
            return super().acquire_token(request, scopes=scopes)

        return "dummy-token"


require_auth = MockedResourceProtector()
if settings.ENABLE_AUTH0_AUTHENTICATION:
    token_validator = validator.Auth0JWTBearerTokenValidator(
        settings.AUTH0_DOMAIN,
        settings.AUTH0_AUDIENCE,
    )
    require_auth.register_token_validator(token_validator)
