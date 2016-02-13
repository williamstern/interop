"""This file provides Python types for the client API.

Most of these types are direct copies of what the interop server API
requires. They include input validation, making a best-effort to ensure
values will be accepted by the server.
"""

import dateutil.parser
import re
import sys


def check_latitude(lat):
    """Assert that latitude is valid.

    Raises:
        ValueError: Latitude out of range
    """
    if lat < -90 or lat > 90:
        raise ValueError('Latitude (%f) out of range [-90 - 90]' % lat)


def check_longitude(lon):
    """Assert that longitude is valid.

    Raises:
        ValueError: Longitude out of range
    """
    if lon < -180 or lon > 180:
        raise ValueError('Longitude (%f) out of range [-180, 180]' % lon)


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
        uas_heading: Aircraft heading (true north) in degrees (0-360).

    Raises:
        ValueError: Argument not convertable to float or out of range.
    """

    def __init__(self, latitude, longitude, altitude_msl, uas_heading):
        super(Telemetry, self).__init__(['latitude', 'longitude',
                                         'altitude_msl', 'uas_heading'])

        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude_msl = float(altitude_msl)
        self.uas_heading = float(uas_heading)

        check_latitude(self.latitude)
        check_longitude(self.longitude)

        if self.uas_heading < 0 or self.uas_heading > 360:
            raise ValueError('Heading (%f) out of range [0, 360]' %
                             self.uas_heading)


class ServerInfo(Serializable):
    """Server information to be displayed to judges.

    Attributes:
        message: Custom message from the server
        message_timestamp (datetime.datetime): Message timestamp
        server_time (datetime.datetime): Current server time

    Raises:
        TypeError, ValueError: Message or server timestamp could not be parsed.
    """

    def __init__(self, message, message_timestamp, server_time):
        super(ServerInfo, self).__init__(['message', 'message_timestamp',
                                          'server_time'])  # yapf: disable

        self.message = message
        self.message_timestamp = dateutil.parser.parse(message_timestamp)
        self.server_time = dateutil.parser.parse(server_time)


class StationaryObstacle(Serializable):
    """A stationary obstacle.

    This obstacle is a cylinder with a given location, height, and radius.

    Attributes:
        latitude: Latitude of the center of the cylinder in decimal degrees
        longitude: Longitude of the center of the cylinder in decimal degrees
        cylinder_radius: Radius in feet
        cylinder_height: Height in feet

    Raises:
        ValueError: Argument not convertable to float or out of range.
    """

    def __init__(self, latitude, longitude, cylinder_radius, cylinder_height):
        super(StationaryObstacle, self).__init__(
            ['latitude', 'longitude', 'cylinder_radius', 'cylinder_height'])

        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.cylinder_radius = float(cylinder_radius)
        self.cylinder_height = float(cylinder_height)

        check_latitude(self.latitude)
        check_longitude(self.longitude)

        if self.cylinder_radius < 0:
            raise ValueError('Cylinder radius (%f) must be non-negative' %
                             self.cylinder_radius)

        if self.cylinder_height < 0:
            raise ValueError('Cylinder height (%f) must be non-negative' %
                             self.cylinder_height)


class MovingObstacle(Serializable):
    """A moving obstacle.

    This obstacle is a sphere with a given location, altitude, and radius.

    Attributes:
        latitude: Latitude of the center of the cylinder in decimal degrees
        longitude: Longitude of the center of the cylinder in decimal degrees
        altitude_msl: Sphere centroid altitude MSL in feet
        sphere_radius: Radius in feet

    Raises:
        ValueError: Argument not convertable to float or out of range.
    """

    def __init__(self, latitude, longitude, altitude_msl, sphere_radius):
        super(MovingObstacle, self).__init__(['latitude', 'longitude',
                                              'altitude_msl', 'sphere_radius'])

        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude_msl = float(altitude_msl)
        self.sphere_radius = float(sphere_radius)

        check_latitude(self.latitude)
        check_longitude(self.longitude)

        if self.sphere_radius < 0:
            raise ValueError('Sphere radius (%f) must be non-negative' %
                             self.sphere_radius)


class Target(Serializable):
    """A target.

    Attributes:
        id: Optional. The ID of the target. Assigned by the interoperability
            server.
        user: Optional. The ID of the user who created the target. Assigned by
            the interoperability server.
        type: Target type, must be one of TargetType.
        latitude: Optional. Target latitude in decimal degrees. If provided,
            longitude must also be provided.
        longitude: Optional. Target longitude in decimal degrees. If provided,
            latitude must also be provided.
        orientation: Optional. Target orientation.
        shape: Optional. Target shape.
        background_color: Optional. Target color.
        alphanumeric: Optional. Target alphanumeric. [0-9, a-z, A-Z].
        alphanumeric_color: Optional. Target alphanumeric color.
        description: Optional. Free-form description of the target, used for
            certain target types.

    Raises:
        ValueError: Argument not valid.
    """

    def __init__(self,
                 id=None,
                 user=None,
                 type=None,
                 latitude=None,
                 longitude=None,
                 orientation=None,
                 shape=None,
                 background_color=None,
                 alphanumeric=None,
                 alphanumeric_color=None,
                 description=None):
        super(Target, self).__init__(
            ['id', 'user', 'type', 'latitude', 'longitude', 'orientation',
             'shape', 'background_color', 'alphanumeric', 'alphanumeric_color',
             'description'])

        self.id = id
        self.user = user
        self.type = type
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.orientation = orientation
        self.shape = shape
        self.background_color = background_color
        self.alphanumeric = alphanumeric
        self.alphanumeric_color = alphanumeric_color
        self.description = description

        if not self.type:
            raise ValueError('Provided target type is invalid.')

        check_latitude(self.latitude)
        check_longitude(self.longitude)

        if (self.alphanumeric and
                not re.match('^[0-9a-zA-Z]$', self.alphanumeric)):
            raise ValueError('Provided alphanumeric is not valid: %s' %
                             self.alphanumeric)
