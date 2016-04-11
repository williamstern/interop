"""Target model."""

import enum
import collections
import networkx as nx
from django.conf import settings
from django.db import models
from gps_position import GpsPosition


class Choices(enum.IntEnum):
    """Base class for enums used to limit Django field choices,
    plus other helper methods.

    Item names should be lowercase to work properly with lookup().
    """

    @classmethod
    def choices(cls):
        """Provide choices for Django's IntField.choices.

        Returns:
            Enum values in an iterator to be passed to IntField.choices.
            The enum value is used as the field key, and the name as the
            description.
        """
        return [(int(v), k) for k, v in cls.__members__.items()]

    @classmethod
    def lookup(cls, s):
        """Lookup value from name.

        Args:
            s: name to lookup; case insensitive

        Returns:
            Value associated with name

        Raises:
            KeyError: name not valid
        """
        return cls.__members__[str(s).lower()]

    @classmethod
    def names(cls):
        """Names of choices

        Returns:
            List of names of values
        """
        return cls.__members__.keys()


@enum.unique
class TargetType(Choices):
    """Valid target types.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    standard = 1
    qrc = 2
    off_axis = 3
    emergent = 4


@enum.unique
class Orientation(Choices):
    """Valid target orientations.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    n = 1
    ne = 2
    e = 3
    se = 4
    s = 5
    sw = 6
    w = 7
    nw = 8


@enum.unique
class Shape(Choices):
    """Valid target shapes.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    circle = 1
    semicircle = 2
    quarter_circle = 3
    triangle = 4
    square = 5
    rectangle = 6
    trapezoid = 7
    pentagon = 8
    hexagon = 9
    heptagon = 10
    octagon = 11
    star = 12
    cross = 13


@enum.unique
class Color(Choices):
    """Valid target colors.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    white = 1
    black = 2
    gray = 3
    red = 4
    blue = 5
    green = 6
    yellow = 7
    purple = 8
    brown = 9
    orange = 10


class Target(models.Model):
    """Target represents a single target submission for a team."""
    # The user which submitted and owns this target.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)

    # Target type.
    target_type = models.IntegerField(choices=TargetType.choices())

    # Target location.
    location = models.ForeignKey(GpsPosition, null=True, blank=True)

    # Target orientation.
    orientation = models.IntegerField(choices=Orientation.choices(),
                                      null=True,
                                      blank=True)

    # Target shape.
    shape = models.IntegerField(choices=Shape.choices(), null=True, blank=True)

    # Target background color.
    background_color = models.IntegerField(choices=Color.choices(),
                                           null=True,
                                           blank=True)

    # Target alphanumeric.
    alphanumeric = models.TextField(default='', blank=True)

    # Target alphanumeric color.
    alphanumeric_color = models.IntegerField(choices=Color.choices(),
                                             null=True,
                                             blank=True)

    # Free-form target description.
    description = models.TextField(default='', blank=True)

    # Target is an ADLC submission.
    autonomous = models.BooleanField(default=False)

    # Uploaded target image thumbnail.
    thumbnail = models.ImageField(upload_to='targets', blank=True)

    # Whether judge considers thumbnail valid for target.
    thumbnail_approved = models.NullBooleanField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        d = self.json()

        return unicode("{name}(pk={id}, user={user}, "
                       "target_type={type}, "
                       "latitude={latitude}, "
                       "longitude={longitude}, "
                       "orientation={orientation}, shape={shape} "
                       "background_color={background_color}, "
                       "alphanumeric='{alphanumeric}', "
                       "alphanumeric_color={alphanumeric_color}, "
                       "description='{description}', "
                       "autonomous='{autonomous}', "
                       "thumbnail='{thumbnail}', "
                       "thumbnail_approved='{thumbnail_approved}')".format(
                           name=self.__class__.__name__,
                           thumbnail=self.thumbnail,
                           thumbnail_approved=str(self.thumbnail_approved),
                           **d))

    def json(self, is_superuser=False):
        """Target as dict, for JSON."""
        target_type = None
        if self.target_type is not None:
            target_type = TargetType(self.target_type).name

        latitude = None
        longitude = None
        if self.location is not None:
            latitude = self.location.latitude
            longitude = self.location.longitude

        orientation = None
        if self.orientation is not None:
            orientation = Orientation(self.orientation).name

        shape = None
        if self.shape is not None:
            shape = Shape(self.shape).name

        background_color = None
        if self.background_color is not None:
            background_color = Color(self.background_color).name

        alphanumeric = None
        if self.alphanumeric != '':
            alphanumeric = self.alphanumeric

        alphanumeric_color = None
        if self.alphanumeric_color is not None:
            alphanumeric_color = Color(self.alphanumeric_color).name

        description = None
        if self.description != '':
            description = self.description

        d = {
            'id': self.pk,
            'user': self.user.pk,
            'type': target_type,
            'latitude': latitude,
            'longitude': longitude,
            'orientation': orientation,
            'shape': shape,
            'background_color': background_color,
            'alphanumeric': alphanumeric,
            'alphanumeric_color': alphanumeric_color,
            'description': description,
            'autonomous': self.autonomous,
        }
        if is_superuser:
            d['thumbnail_approved'] = self.thumbnail_approved
        return d

    def similar_classifications(self, other):
        """Counts the number of similar classification attributes.

        Args:
            other: Another target for which to compare.
        Returns:
            The ratio of attributes which are the same.
        """
        if self.type != other.type:
            return 0

        standard_fields = ['orientation', 'shape', 'background_color',
                           'alphanumeric', 'alphanumeric_color'],
        classify_fields = {
            TargetType.standard: standard_fields,
            TargetType.qrc: ['description'],
            TargetType.off_axis: standard_fields,
            TargetType.emergent: [],
        }
        fields = classify_fields[self.type]
        count = 0
        for field in fields:
            if getattr(self, field) == getattr(other, field):
                count += 1
        return float(count) / len(fields) if fields else 1


class TargetEvaluator(object):
    """Evaluates submitted targets against real judge-made targets."""

    def __init__(self, submitted_targets, real_targets):
        """Creates an evaluation of submitted targets against real targets.

        Args:
            submitted_targets: List of submitted Target objects.
            real_targets: List of real Target objects made by judges.
        """
        self.submitted_targets = submitted_targets
        self.real_targets = real_targets
        self.matches = self.match_targets(submitted_targets, real_targets)

    def match_value(self, submitted, real):
        """Computes the match value if the two targets were paired.

        Args:
            submitted: The team submitted target.
            real: The real target made by the judges.
        Returns:
            The match value, which is proportional to the points a team would
            receive if the targets were paired.
        """
        # Targets which are not the same type have no match value.
        # Targets which don't have an approved image have no match value.
        if submitted.type != real.type or not submitted.thumbnail_approved:
            return 0

        # Compute the classification point value.
        i = bisect.bisect_right(settings.TARGET_CLASSIFY_VALUE,
                                real.similar_classifications(submitted))
        classify_value = settings.TARGET_CLASSIFY_VALUE[i - 1] if i else 0
        if not classify_value:
            # Targets which don't have threshold classification have no value.
            return 0

        # Compute the location value.
        i = bisect.bisect_left(settings.TARGET_LOCATION_VALUE,
                               submitted.location.distance_to(real.location))
        location_value = settings.TARGET_LOCATION_VALUE[i] if i != len(
            settings.TARGET_LOCATION_VALUE) else 0

        return classify_value + location_value

    def match_targets(self, submitted_targets, real_targets):
        """Matches the targets to maximize match value.

        Args:
            submitted_targets: List of submitted Target objects.
            real_targets: List of real Target objects made by judges.
        Returns:
            A map from submitted target to real target, and real target to
            submitted target.
        """
        # Create a bipartite graph from submitted to real targets with match
        # values as edge weights. Skip edges with no match value.
        g = nx.Graph()
        g.add_nodes_from(submitted_targets, bipartite=0)
        g.add_nodes_from(real_targets, bipartite=1)
        for submitted in submitted_targets:
            for real in real_targets:
                match_value = self.match_value(submitted, real)
                if match_value:
                    g.add_edge(submitted, real, weight=match_value)
        # Compute the full matching
        return nx.bipartite.maximum_matching(g)

    def evaluation_dict(self):
        """Gets the evaluation dictionary.

        Returns:
            A dictionary of the form:
            {
                'matched_target_value': Total value from matched targets
                'unmatched_target_count': Count of unmatched targets
                'targets': {
                    'pk': {
                        'match_value': the value for the target
                        'image_approved': whether the image was approved
                        'classifications': number of similar classifications
                        'location_accuracy': distance from actual
                    }
                }
            }
        """
        matched_target_value = 0
        unmatched_target_count = 0
        target_dict = collections.defaultdict(dict)

        for submitted in self.submitted_targets:
            real = self.matches[submitted]
            match_value = 0
            classifications = 0
            location_accuracy = -1
            if not real:
                unmatched_target_count += 1
            else:
                match_value = self.match_value(submitted, real)
                classifications = submitted.similar_classifications(real)
                location_accuracy = submitted.location.distance_to(
                    real.location)
            matched_target_value += match_value
            target_dict[submitted.pk] = {
                'match_value': match_value,
                'image_approved': submitted.thumbnail_approved,
                'classifications': classifications,
                'location_accuracy': location_accuracy,
            }

        return {
            'matched_target_value': matched_target_value,
            'unmatched_target_count': unmatched_target_count,
            'targets': target_dict,
        }
