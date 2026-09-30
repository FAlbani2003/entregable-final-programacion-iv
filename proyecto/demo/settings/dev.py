import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True") == "True"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-pgsk-rj@)k7jfao&58)aj7l%z7&c%!x)f7devz3rb*ca)f4ol)",
)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# En HTTP (sin HTTPS) Chrome descarta la página si llega este encabezado
# y la pestaña queda en blanco, sin título.
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
