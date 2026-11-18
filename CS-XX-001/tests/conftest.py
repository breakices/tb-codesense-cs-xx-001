import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

os.environ["DJANGO_SETTINGS_MODULE"] = "cs_settings"


def pytest_configure(config):
    import django

    django.setup()
