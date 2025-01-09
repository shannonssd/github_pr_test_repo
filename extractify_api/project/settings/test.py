import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

DEBUG = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 3600
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ENABLE_AUTH0_AUTHENTICATION = bool(strtobool(os.getenv("ENABLE_AUTH0_AUTHENTICATION", "True")))

ALLOWED_CIDR_NETS = (
    os.getenv("ALLOWED_CIDR_NETS", "").split(",")
    if os.getenv("ALLOWED_CIDR_NETS") is not None
    else []
)

if ENABLE_SENTRY:
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[DjangoIntegration()], environment="staging"  # noqa: F405
    )
