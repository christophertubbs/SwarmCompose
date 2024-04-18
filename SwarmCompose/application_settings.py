"""
A module for declaring application values that may be accessed without launching a Django instance
"""
import os

from pathlib import Path
from datetime import datetime

from dateutil import tz

import utils

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SWARM_COMPOSE_SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('SWARM_COMPOSE_SQL_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('SWARM_COMPOSE_SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SWARM_COMPOSE_SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SWARM_COMPOSE_SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SWARM_COMPOSE_SQL_PORT', '5432'),
    }
}

DEBUG = utils.is_true(
    os.environ.get(
        'DEBUG_SWARM_COMPOSE',
        True
    )
)

TIME_ZONE = os.environ.get(
    "SWARM_COMPOSE_TIME_ZONE",
    #tz.tzlocal().tzname(datetime.now().astimezone())
    "America/Chicago"
)

DATETIME_FORMAT = '%Y-%m-%d %H:%M%z'

