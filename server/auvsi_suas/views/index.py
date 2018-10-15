"""Index page admin view."""

import logging
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class Index(TemplateView):
    """Main view for users connecting via web browsers.

    This view downloads and displays a JS view. This view first logs in the
    user. If the user is a superuser, it shows the Judging view which is used
    to manage the competition and evaluate teams.
    """

    template_name = 'index.html'

    # Use user_passes_test to redirect to login rather than return 403.
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        return context
