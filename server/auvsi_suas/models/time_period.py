class TimePeriod(object):
    """
    Describe a continuous period of time.
    A value of None indicates infinity. Both start and end are inclusive.
    """

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
