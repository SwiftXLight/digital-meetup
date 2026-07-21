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
