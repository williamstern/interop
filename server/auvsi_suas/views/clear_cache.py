"""Admin view to clear the cache."""

from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpResponse


@user_passes_test(lambda u: u.is_superuser)
def clear_cache(request):
    """Clears the cache on admin's request."""
    logger.info('Admin requested to clear the cache.')
    cache.clear()
    return HttpResponse("Cache cleared.")
