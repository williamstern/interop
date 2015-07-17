"""Test runner which uses a different filepattern."""

from django.test import runner


class AuvsiSuasTestRunner(runner.DiscoverRunner):
    def __init__(self, *args, **kwargs):
        """Initializes the parent with a different filepattern."""
        kwargs['pattern'] = '*_test.py'
        super(AuvsiSuasTestRunner, self).__init__(*args, **kwargs)
