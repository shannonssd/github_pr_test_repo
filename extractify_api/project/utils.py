import os


def is_live_environment() -> bool:
    """Return boolean whether a live production environment is set."""
    return os.getenv("DJANGO_SETTINGS_MODULE", "").endswith("settings.live")
