"""Target model."""

import collections
import enum
import networkx as nx
import operator
from django.conf import settings
from django.db import models
from gps_position import GpsPosition
from takeoff_or_landing_event import TakeoffOrLandingEvent


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

    # Time that this target was first created.
    # auto_now_add automatically sets this field on initial creation.
    creation_time = models.DateTimeField(auto_now_add=True)

    # Time that this target was last modified.
    # auto_now automatically updates this field on save().
    last_modified_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        d = self.json(is_superuser=True)
        return unicode('{name}({fields})'.format(
            name=self.__class__.__name__,
            fields=', '.join('%s=%s' % (k, v) for k, v in d.iteritems())))

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
            d['thumbnail'] = self.thumbnail.name if self.thumbnail else None
            d['thumbnail_approved'] = self.thumbnail_approved
            d['creation_time'] = self.creation_time
            d['last_modified_time'] = self.last_modified_time

        return d

    def similar_classifications(self, other):
        """Counts the number of similar classification attributes.

        Args:
            other: Another target for which to compare.
        Returns:
            The ratio of attributes which are the same.
        """
        # Cannot have similar fields with different type targets.
        if self.target_type != other.target_type:
            return 0

        standard_fields = ['orientation', 'shape', 'background_color',
                           'alphanumeric', 'alphanumeric_color']
        classify_fields = {
            TargetType.standard: standard_fields,
            TargetType.qrc: ['description'],
            TargetType.off_axis: standard_fields,
            TargetType.emergent: [],
        }
        fields = classify_fields[self.target_type]
        count = 0
        for field in fields:
            if getattr(self, field) == getattr(other, field):
                count += 1
        return float(count) / len(fields) if fields else 1

    def actionable_submission(self, flights=None):
        """Checks if Target meets Actionable Intelligence submission criteria.

        A target is "actionable" if the aircraft was in flight from initial
        target submission until the last update. Note that this does not check
        the localization or characterization Actionable Intelligence criteria.

        Args:
            flights: Optional memoized flights for this target's user. If
                     omitted, the flights will be looked up.

        Returns:
            True if target may be considered an "actionable" submission.
        """
        if flights is None:
            flights = TakeoffOrLandingEvent.flights(self.user)

        for flight in flights:
            if flight.within(self.creation_time) and \
                flight.within(self.last_modified_time):
                return True

        return False


class TargetEvaluator(object):
    """Evaluates submitted targets against real judge-made targets."""

    def __init__(self, submitted_targets, real_targets):
        """Creates an evaluation of submitted targets against real targets.

        Args:
            submitted_targets: List of submitted Target objects, all from
                               the same user.
            real_targets: List of real Target objects made by judges.

        Raises:
            AssertionError: not all submitted targets are from the same user.
        """
        self.submitted_targets = submitted_targets
        self.real_targets = real_targets

        if self.submitted_targets:
            self.user = self.submitted_targets[0].user
            for t in self.submitted_targets:
                if t.user != self.user:
                    raise AssertionError(
                        "All submitted targets must be from the same user")

            self.flights = TakeoffOrLandingEvent.flights(self.user)

        self.matches = self.match_targets(submitted_targets, real_targets)

    def actionable(self, target, classifications, location_accuracy):
        """Determines level of target actionable intelligence.

        Args:
            target: Target to test
            classifications: Number of correct classifications
            location_accuracy: Target location accuracy

        Returns:
            Threshold met: one of None, 'threshold', or 'objective'
        """
        if target.target_type == TargetType.standard and \
            target.actionable_submission(flights=self.flights):
            params = settings.TARGET_ACTIONABLE_PARAMS
            if classifications >= params['objective']['characteristics'] \
                and location_accuracy <= params['objective']['location']:
                return 'objective'
            elif classifications >= params['objective']['characteristics'] \
                and location_accuracy <= params['objective']['location']:
                return 'threshold'

        return None

    def range_lookup(self,
                     ranges,
                     key,
                     start_operator=operator.ge,
                     end_operator=operator.le):
        """Performs a range based lookup.

        Args:
            ranges: A list of maps containing start,end,value keys.
            key: The key for the range lookup.
            start_operator: The operator to compare the start key against.
            end_operator: The operator to compare the end key against.
        Returns:
            The value associated for the range lookup, or None if not in range.
        """
        for r in ranges:
            if start_operator(key, r['start']) and end_operator(key, r['end']):
                return r['value']
        return None

    def match_value(self, submitted, real):
        """Computes the match value if the two targets were paired.

        Args:
            submitted: The team submitted target. Must be one of
                self.submitted_targets.
            real: The real target made by the judges. Must be one of
                self.real_targets.
        Returns:
            The match value, which is proportional to the points a team would
            receive if the targets were paired.
        """
        # Targets which are not the same type have no match value.
        # Targets which don't have an approved image have no match value.
        if (submitted.target_type != real.target_type or
                not submitted.thumbnail_approved):
            return 0

        # Compute the classification point value.
        num_similar = real.similar_classifications(submitted)
        classify_value = self.range_lookup(settings.TARGET_CLASSIFY_RANGES,
                                           num_similar,
                                           end_operator=operator.lt)
        if not classify_value:
            # Targets which don't have threshold classification have no value.
            return 0

        # Compute the location value.
        location_dist = submitted.location.distance_to(real.location)
        location_value = self.range_lookup(settings.TARGET_LOCATION_RANGES,
                                           location_dist,
                                           start_operator=operator.gt)

        # Actionable intelligence value
        actionable = self.actionable(submitted, num_similar, location_dist)
        if actionable == 'objective':
            actionable_value = \
                settings.TARGET_ACTIONABLE_PARAMS['objective']['value']
        elif actionable == 'threshold':
            actionable_value = \
                settings.TARGET_ACTIONABLE_PARAMS['threshold']['value']
        else:
            actionable_value = 0

        return classify_value + location_value + actionable_value

    def match_targets(self, submitted_targets, real_targets):
        """Matches the targets to maximize match value.

        Args:
            submitted_targets: List of submitted Target objects.
            real_targets: List of real Target objects made by judges.
        Returns:
            A map from submitted target to real target, and real target to
            submitted target, if they are matched.
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
                    pk: {
                        'submitted_target': The pk of the submitted target.
                        'match_value': the value for the target
                        'image_approved': whether the image was approved
                        'classifications': proportion of similar classifications
                        'location_accuracy': distance from actual
                        'actionable': level of Actionable Intelligence criteria
                            met: one of False, 'threshold', or 'objective'
                    }
                }
            }
        """
        matched_target_value = 0
        target_dict = collections.defaultdict(dict)
        for real in self.real_targets:
            submitted = self.matches.get(real)
            if submitted:
                match_value = self.match_value(submitted, real)
                matched_target_value += match_value

                classifications = submitted.similar_classifications(real)
                location_accuracy = submitted.location.distance_to(
                    real.location)
                actionable = self.actionable(submitted, classifications,
                                             location_accuracy)

                target_dict[real.pk] = {
                    'submitted_target': submitted.pk,
                    'match_value': match_value,
                    'image_approved': submitted.thumbnail_approved,
                    'classifications': classifications,
                    'location_accuracy': location_accuracy,
                    'actionable': actionable,
                }
            else:
                target_dict[real.pk] = {
                    'submitted_target': '',
                    'match_value': '',
                    'image_approved': '',
                    'classifications': '',
                    'location_accuracy': '',
                    'actionable': '',
                }

        unmatched_targets = len(self.submitted_targets) - len(self.matches) / 2
        return {
            'matched_target_value': matched_target_value,
            'unmatched_target_count': unmatched_targets,
            'targets': target_dict,
        }
