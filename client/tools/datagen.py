"""Data generation interface for tools acting as a UAS."""

import abc
import logging

from interop import Telemetry


class DataGenerator(object):
    """Base class for a data generator which creates UAS telemetry."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_uas_telemetry(self, cur_time):
        """Gets the UAS telemetry position at the given time.

        Args:
            cur_time: The time to get UAS telemetry at.
        Returns:
            A tuple (latitude, longitude, altitude_msl, uas_heading) where
            the values are in degrees, degrees, feet, degrees respectively.
        """
        logging.Fatal('Unimplemented.')


class ZeroValueGenerator(DataGenerator):
    """Generates zero values for all of time."""

    def get_uas_telemetry(self, cur_time):
        """Overrides base method."""
        return Telemetry(0, 0, 0, 0)
