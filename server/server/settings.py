"""
Django settings for the interop server.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'anp#d4lgo3u6j&6dc3+8sn!t+l(6hcuspm^&3(yq10evfwbh+1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Public IP addresses given access to Django Debug Toolbar
# Add your IP here, if not localhost.
INTERNAL_IPS = ['127.0.0.1']

# Application definition
INSTALLED_APPS = (
    'auvsi_suas',
    'auvsi_suas.views.auvsi_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'pipeline',
)  # yapf: disable

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auvsi_suas.views.middleware.LoggingMiddleware',
)  # yapf: disable

ROOT_URLCONF = 'server.urls'
WSGI_APPLICATION = 'server.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'auvsi_suas_db',
        'USER': 'postgresql_user',
        'PASSWORD': 'postgresql_pass',
        'CONN_MAX_AGE': None,
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_auvsi_suas_db',
        },
    }
}

# Caches
# https://docs.djangoproject.com/en/1.11/topics/cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 10,
        'KEY_PREFIX': 'suas',
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
            '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['file'],
        },
        'django': {
            'handlers': ['file'],
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'auvsi_suas.views': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'auvsi_suas/frontend'),
]

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE = {
    'STYLESHEETS': {
        'styles': {
            'source_filenames': (
                'third_party/foundation/css/foundation.min.css',
                'third_party/foundation/css/normalize.css',
                'app.css',
                'components/mission-map/mission-map.css',
                'components/team-status/team-status.css',
                'pages/mission-dashboard/mission-dashboard.css',
                'pages/mission-list/mission-list.css',
                'pages/odlc-review/odlc-review.css',
                'pages/evaluate-teams/evaluate-teams.css',
            ),
            'output_filename': 'styles.css',
        },
    },
    'JAVASCRIPT': {
        'scripts': {
            'source_filenames': (
                'third_party/foundation/js/fastclick.js',
                'third_party/foundation/js/jquery.js',
                'third_party/foundation/js/jquery.cookie.js',
                'third_party/foundation/js/modernizr.js',
                'third_party/foundation/js/placeholder.js',
                'third_party/foundation/js/foundation.min.js',
                'third_party/foundation/js/foundation.accordion.js',
                'third_party/foundation/js/foundation.alert.js',
                'third_party/foundation/js/foundation.dropdown.js',
                'third_party/foundation/js/foundation.tooltip.js',
                'third_party/foundation/js/foundation.topbar.js',
                'third_party/threejs/three.js',
                'third_party/angularjs/angular.js',
                'third_party/angularjs/angular-cookies.js',
                'third_party/angularjs/angular-resource.js',
                'third_party/angularjs/angular-route.js',
                'third_party/angularjs/angular-sanitize.js',
                'third_party/angularjs/angular-touch.js',
                'app.js',
                'components/settings/settings-service.js',
                'components/navigation/navigation.js',
                'components/backend/backend-service.js',
                'components/units/units-service.js',
                'components/distance/distance-service.js',
                'components/mission-scene/mission-scene.js',
                'components/mission-map/mission-map-controller.js',
                'components/team-status/team-status-controller.js',
                'pages/mission-dashboard/mission-dashboard-controller.js',
                'pages/mission-list/mission-list-controller.js',
                'pages/odlc-review/odlc-review-controller.js',
                'pages/evaluate-teams/evaluate-teams-controller.js',
            ),
            'output_filename': 'scripts.js',
        },
    },
} # yapf: disable

# User uploaded files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media'

# Send images with sendfile.
SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = MEDIA_URL

# Login URL
LOGIN_URL = '/admin/login/?next=/'

# Migrations
MIGRATION_MODULES = {
    'auvsi_suas.models': 'auvsi_suas.models.migrations',
}  # yapf: disable

# Custom test runner.
TEST_RUNNER = 'auvsi_suas.test_runner.AuvsiSuasTestRunner'

# Whether tests can/should generate plots (requires window access)
TEST_ENABLE_PLOTTING = False

# The time window (in seconds) in which a plane cannot be counted as going out
# of bounds multiple times. This prevents noisy input data from recording
# significant more violations than a human observer.
OUT_OF_BOUNDS_DEBOUNCE_SEC = 10.0
# The max distance for a waypoint to be considered satisfied.
SATISFIED_WAYPOINT_DIST_MAX_FT = 100

# The time between interop telemetry posts that's a prereq for other tasks.
INTEROP_TELEM_THRESHOLD_TIME_SEC = 1.0

# Ratio of object points to lose for every extra unmatched object submitted.
EXTRA_OBJECT_PENALTY_RATIO = 0.05
# The weight of classification accuracy when calculating a odlc match score.
CHARACTERISTICS_WEIGHT = 0.2
# The lowest allowed location accuracy (in feet)
TARGET_LOCATION_THRESHOLD = 150
# The weight of geolocation accuracy when calculating a odlc match score.
GEOLOCATION_WEIGHT = 0.3
# The weight of actionable intelligence when calculating a odlc match score.
ACTIONABLE_WEIGHT = 0.3
# The weight of autonomy when calculating a odlc match score.
AUTONOMY_WEIGHT = 0.2

# Weight of timeline points for mission time.
MISSION_TIME_WEIGHT = 0.8
# Weight of timeline points for not taking a timeout.
TIMEOUT_WEIGHT = 0.2
# Max mission time.
MISSION_MAX_TIME_SEC = 45.0 * 60.0
# Points for flight time in mission time score.
FLIGHT_TIME_SEC_TO_POINTS = 5.0 / 60.0
# Points for post-processing time in mission time score.
PROCESS_TIME_SEC_TO_POINTS = 1.0 / 60.0
# Total points possible for mission time.
MISSION_TIME_TOTAL_POINTS = MISSION_MAX_TIME_SEC * max(
    FLIGHT_TIME_SEC_TO_POINTS, PROCESS_TIME_SEC_TO_POINTS)
# Mission time points lost due for every second over time.
MISSION_TIME_PENALTY_FROM_SEC = 0.03

# Ratio of points lost per takeover.
AUTONOMOUS_FLIGHT_TAKEOVER = 0.10
# Ratio of points lost per out of bounds.
BOUND_PENALTY = 0.1
SAFETY_BOUND_PENALTY = 0.1
# Ratio of points lost for TFOA and crash.
TFOA_PENALTY = 0.25
CRASH_PENALTY = 0.35
# Weight of flight points to all autonomous flight.
AUTONOMOUS_FLIGHT_FLIGHT_WEIGHT = 0.4
# Weight of capture points to all autonomous flight.
WAYPOINT_CAPTURE_WEIGHT = 0.1
# Weight of accuracy points to all autonomous flight.
WAYPOINT_ACCURACY_WEIGHT = 0.5

# Weight of stationary obstacle avoidance.
STATIONARY_OBST_WEIGHT = 0.5
# Weight of moving obstacle avoidance.
MOVING_OBST_WEIGHT = 0.5

# Air delivery accuracy threshold.
AIR_DELIVERY_THRESHOLD_FT = 150.0

# Scoring weights.
TIMELINE_WEIGHT = 0.1
AUTONOMOUS_WEIGHT = 0.3
OBSTACLE_WEIGHT = 0.2
OBJECT_WEIGHT = 0.2
AIR_DELIVERY_WEIGHT = 0.1
OPERATIONAL_WEIGHT = 0.1

# Max aircraft airspeed in ft/s. Rules specify 70 KIAS.
MAX_AIRSPEED_FT_PER_SEC = 118.147
# Maximum interval between telemetry logs allowed for interpolation.
MAX_TELMETRY_INTERPOLATE_INTERVAL_SEC = 1.5
