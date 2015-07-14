"""This file provides Python types for the client API.

Most of these types are direct copies of what the interop server API
requires. They include input validation, making a best-effort to ensure
values will be accepted by the server.
"""


class Serializable(object):
    """ Serializable is a simple base class which provides basic
    'serialization' (a simple dict) of a subset of attributes the inheriting
    class.

    By serializing only specified attributes, other attributes can be utilized
    by the class (or its subclasses) without being included in the serialized
    dict.
    """

    def __init__(self, attrs):
        """Initialize attributes to serialize

        Args:
            attrs: List of string attribute names to serialize.
        """
        self.attrs = attrs

    def serialize(self):
        """Serialize the current state of the object."""
        return {k: self.__dict__[k] for k in self.attrs}


class Telemetry(Serializable):
    """UAS Telemetry at a single point in time.

    Attributes:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        altitude_msl: Altitude MSL in feet.
        uas_heading: Aircraft heading in degrees (0-360).

    Raises:
        ValueError: Argument not convertable to float or out of range.
    """

    def __init__(self, latitude, longitude, altitude_msl, uas_heading):
        super(Telemetry, self).__init__(["latitude", "longitude",
                                         "altitude_msl", "uas_heading"])

        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude_msl = float(altitude_msl)
        self.uas_heading = float(uas_heading)

        if self.latitude < -90 or self.latitude > 90:
            raise ValueError("Latitude (%f) out of range [-90 - 90]" %
                             self.latitude)

        if self.longitude < -180 or self.longitude > 180:
            raise ValueError("Longitude (%f) out of range [-180, 180]" %
                             self.longitude)

        if self.uas_heading < 0 or self.uas_heading > 360:
            raise ValueError("Heading (%f) out of range [0, 360]" %
                             self.uas_heading)
