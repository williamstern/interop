"""Index page admin view."""

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


# We want a real redirect to the login page rather than a 403, so
# we use user_passes_test directly.
@user_passes_test(lambda u: u.is_superuser)
def index(request):
    """Main view for users connecting via web browsers.

    This view downloads and displays a JS view. This view first logs in the
    user. If the user is a superuser, it shows the Judging view which is used
    to manage the competition and evaluate teams.
    """
    return render(request, 'auvsi_suas/index.html')
