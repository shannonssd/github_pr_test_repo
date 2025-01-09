import socket

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

DEBUG = True

ENABLE_AUTH0_AUTHENTICATION = bool(strtobool(os.getenv("ENABLE_AUTH0_AUTHENTICATION", "False")))

# Set internal ip address for django debug toolbar
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

if ENABLE_SENTRY:
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[DjangoIntegration()], environment="develop"  # noqa: F405
    )


GOOGLE_APPLICATION_CREDENTIALS = (
    Path(BASE_DIR).resolve() / "keys/google_cloud_service_account_credential.json"
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(GOOGLE_APPLICATION_CREDENTIALS)
