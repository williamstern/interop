"""This file provides Python types for the client API.

Most of these types are direct copies of what the interop server API
requires. They include input validation, making a best-effort to ensure
values will be accepted by the server.
"""


class ClientBaseType(object):
    """ ClientBaseType is a simple base class which provides basic functions.

    The attributes are obtained from the 'attrs' property, which should be
    defined by subclasses.
    """

    # Subclasses should override.
    attrs = []

    def __eq__(self, other):
        """Compares two objects."""
        for attr in self.attrs:
            if self.__dict__[attr] != other.__dict__[attr]:
                return False
        return True

    def __repr__(self):
        """Gets string encoding of object."""
        return "%s(%s)" % (self.__class__.__name__,
                           ', '.join('%s=%s' % (attr, self.__dict__[attr])
                                     for attr in self.attrs))

    def __unicode__(self):
        """Gets unicode encoding of object."""
        return unicode(self.__str__())

    def serialize(self):
        """Serialize the current state of the object."""
        serial = {}
        for attr in self.attrs:
            data = self.__dict__[attr]
            if isinstance(data, ClientBaseType):
                serial[attr] = data.serialize()
            elif isinstance(data, list):
                serial[attr] = [d.serialize() for d in data]
            elif data is not None:
                serial[attr] = data
        return serial

    @classmethod
    def deserialize(cls, d):
        """Deserialize the state of the object."""
        if isinstance(d, cls):
            return d
        else:
            return cls(**d)


class Odlc(ClientBaseType):
    """An odlc.

    Attributes:
        id: Optional. The ID of the odlc. Assigned by the interoperability
            server.
        user: Optional. The ID of the user who created the odlc. Assigned by
            the interoperability server.
        type: Odlc type, must be one of OdlcType.
        latitude: Optional. Odlc latitude in decimal degrees. If provided,
            longitude must also be provided.
        longitude: Optional. Odlc longitude in decimal degrees. If provided,
            latitude must also be provided.
        orientation: Optional. Odlc orientation.
        shape: Optional. Odlc shape.
        background_color: Optional. Odlc color.
        alphanumeric: Optional. Odlc alphanumeric. [0-9, a-z, A-Z].
        alphanumeric_color: Optional. Odlc alphanumeric color.
        description: Optional. Free-form description of the odlc, used for
            certain odlc types.
        autonomous: Optional; defaults to False. Indicates that this is an
            ADLC odlc.
        team_id: Optional. The username of the team on whose behalf to submit
            odlcs. Must be admin user to specify.
        actionable_override: Optional. Manually sets the odlc to be
            actionable. Must be admin user to specify.

    Raises:
        ValueError: Argument not valid.
    """

    attrs = [
        'id', 'user', 'type', 'latitude', 'longitude', 'orientation', 'shape',
        'background_color', 'alphanumeric', 'alphanumeric_color',
        'description', 'autonomous', 'team_id', 'actionable_override'
    ]

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
                 description=None,
                 autonomous=False,
                 team_id=None,
                 actionable_override=None):
        self.id = id
        self.user = user
        self.type = type
        self.latitude = float(latitude) if latitude is not None else None
        self.longitude = float(longitude) if longitude is not None else None
        self.orientation = orientation
        self.shape = shape
        self.background_color = background_color
        self.alphanumeric = alphanumeric
        self.alphanumeric_color = alphanumeric_color
        self.description = description
        self.autonomous = autonomous
        self.actionable_override = actionable_override
        self.team_id = team_id
