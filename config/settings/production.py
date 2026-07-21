from pathlib import Path

from .base import *  # noqa: F403

DEBUG = False

MEDIA_ROOT = Path(env("MEDIA_ROOT", default=str(BASE_DIR / "media")))  # noqa: F405

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

render_hostname = env("RENDER_EXTERNAL_HOSTNAME", default="")  # noqa: F405
if render_hostname:
    if render_hostname not in ALLOWED_HOSTS:  # noqa: F405
        ALLOWED_HOSTS.append(render_hostname)  # noqa: F405

    render_origin = f"https://{render_hostname}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)
