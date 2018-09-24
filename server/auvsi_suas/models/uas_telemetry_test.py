"""Tests for the uas_telemetry module."""

import iso8601
import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from simplekml import Kml

from auvsi_suas.models import units
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.models.waypoint import Waypoint
from auvsi_suas.models import distance
from auvsi_suas.proto.mission_pb2 import WaypointEvaluation


class TestUasTelemetryBase(TestCase):
    """Base for the UasTelemetry tests."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()
        self.now = timezone.now()

    def create_log_element(self, timestamp, lat, lon, alt, heading, user=None):
        if user is None:
            user = self.user

        pos = GpsPosition(latitude=lat, longitude=lon)
        pos.save()
        apos = AerialPosition(gps_position=pos, altitude_msl=alt)
        apos.save()
        log = UasTelemetry(user=user, uas_position=apos, uas_heading=heading)
        log.save()
        log.timestamp = self.now + datetime.timedelta(seconds=timestamp)
        log.save()
        return log

    def create_uas_logs(self, entries, user=None):
        """Create a list of uas telemetry logs.

        Args:
            entries: List of (t, lat, lon, alt, heading) tuples for each entry.
            user: User to create logs for.

        Returns:
            List of UasTelemetry objects
        """
        if user is None:
            user = self.user

        ret = []
        for (t, lat, lon, alt, head) in entries:
            ret.append(self.create_log_element(t, lat, lon, alt, head, user))
        return ret

    def waypoints_from_data(self, waypoints_data):
        """Converts tuples of lat/lon/alt to a waypoint."""
        waypoints = []
        for i, waypoint in enumerate(waypoints_data):
            (lat, lon, alt) = waypoint
            pos = GpsPosition()
            pos.latitude = lat
            pos.longitude = lon
            pos.save()
            apos = AerialPosition()
            apos.altitude_msl = alt
            apos.gps_position = pos
            apos.save()
            wpt = Waypoint()
            wpt.position = apos
            wpt.order = i
            wpt.save()
            waypoints.append(wpt)
        return waypoints

    def assertTelemetryEqual(self, expect, got):
        """Assert two telemetry are equal."""
        msg = '%s != %s' % (expect, got)
        self.assertAlmostEqual(
            expect.uas_position.gps_position.latitude,
            got.uas_position.gps_position.latitude,
            places=6,
            msg=msg)
        self.assertAlmostEqual(
            expect.uas_position.gps_position.longitude,
            got.uas_position.gps_position.longitude,
            places=6,
            msg=msg)
        self.assertAlmostEqual(
            expect.uas_position.altitude_msl,
            got.uas_position.altitude_msl,
            places=3,
            msg=msg)
        self.assertAlmostEqual(
            expect.uas_heading, got.uas_heading, places=3, msg=msg)

    def assertTelemetriesEqual(self, expect, got):
        "Assert two lists of telemetry are equal." ""
        expect = [i for i in expect]
        got = [i for i in got]
        self.assertEqual(len(expect), len(got))
        for ix in range(len(expect)):
            self.assertTelemetryEqual(expect[ix], got[ix])

    def assertSatisfiedWaypoints(self, expect, got):
        """Assert two satisfied_waypoints return values are equal."""
        msg = '%s != %s' % (expect, got)
        self.assertEqual(len(expect), len(got), msg=msg)
        for i in range(len(expect)):
            e = expect[i]
            g = got[i]
            self.assertEqual(e.id, g.id, msg=msg)
            self.assertAlmostEqual(
                e.score_ratio, g.score_ratio, places=2, msg=msg)
            self.assertAlmostEqual(
                e.closest_for_scored_approach_ft,
                g.closest_for_scored_approach_ft,
                delta=5,
                msg=msg)
            self.assertAlmostEqual(
                e.closest_for_mission_ft,
                g.closest_for_mission_ft,
                delta=5,
                msg=msg)


class TestUasTelemetry(TestUasTelemetryBase):
    """Tests the UasTelemetry model."""

    def setUp(self):
        super(TestUasTelemetry, self).setUp()

        self.log = self.create_log_element(
            timestamp=0, lat=10, lon=100, alt=200, heading=90)

    def test_str(self):
        """Tests the str method executes."""
        self.assertTrue(str(self.log))

    def test_duplicate_unequal(self):
        """Tests duplicate function with unequal telemetry."""
        log1 = self.create_log_element(
            timestamp=0, lat=20, lon=200, alt=200, heading=90)
        log2 = self.create_log_element(
            timestamp=0, lat=10, lon=100, alt=300, heading=90)
        log3 = self.create_log_element(
            timestamp=0, lat=10, lon=100, alt=200, heading=10)

        self.assertFalse(self.log.duplicate(log1))
        self.assertFalse(self.log.duplicate(log2))
        self.assertFalse(self.log.duplicate(log3))

    def test_duplicate_equal(self):
        """Tests duplicate function with equal telemetry."""
        log1 = self.create_log_element(
            timestamp=0, lat=10, lon=100, alt=200, heading=90)

        self.assertTrue(self.log.duplicate(self.log))
        self.assertTrue(self.log.duplicate(log1))

    def test_json(self):
        """Tests JSON-style output."""
        data = self.log.json()

        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('timestamp', data)
        self.assertIn('latitude', data)
        self.assertIn('longitude', data)
        self.assertIn('altitude_msl', data)
        self.assertIn('heading', data)

        # Timestamp is valid ISO 8601, with timezone
        iso8601.parse_date(data['timestamp'])

        self.assertEqual(10, data['latitude'])
        self.assertEqual(100, data['longitude'])
        self.assertEqual(200, data['altitude_msl'])
        self.assertEqual(90, data['heading'])


class TestUasTelemetryFilter(TestUasTelemetryBase):
    def setUp(self):
        super(TestUasTelemetryFilter, self).setUp()

        self.log1 = self.create_log_element(
            timestamp=0, lat=10, lon=200, alt=200, heading=90)
        self.log2 = self.create_log_element(
            timestamp=0, lat=20, lon=200, alt=200, heading=90)
        self.log3 = self.create_log_element(
            timestamp=0, lat=30, lon=200, alt=200, heading=90)
        self.log4 = self.create_log_element(
            timestamp=0, lat=40, lon=200, alt=200, heading=90)
        self.log5 = self.create_log_element(
            timestamp=0, lat=0, lon=0, alt=0, heading=0)

    def test_no_logs(self):
        """Tests empty log."""
        self.assertEqual(UasTelemetry.dedupe([]), [])

    def test_no_duplicates(self):
        """Tests no duplicates in list."""
        orig = [self.log1, self.log2, self.log3, self.log4]
        self.assertEqual(UasTelemetry.dedupe(orig), orig)

    def test_boundary_duplicates(self):
        """Tests duplicates on the bounds of the list."""
        orig = [self.log1, self.log1, self.log2, self.log2, self.log2]
        expect = [self.log1, self.log2]
        self.assertEqual(UasTelemetry.dedupe(orig), expect)

    def test_duplicates(self):
        orig = [
            self.log1, self.log1, self.log2, self.log3, self.log3, self.log4,
            self.log4
        ]
        expect = [self.log1, self.log2, self.log3, self.log4]
        self.assertEqual(UasTelemetry.dedupe(orig), expect)

    def test_filter_bad(self):
        """Tests filter_bad()."""
        orig = [self.log1, self.log5]
        expect = [self.log1]
        self.assertEqual(list(UasTelemetry.filter_bad(orig)), expect)


class TestUasTelemetryInterpolate(TestUasTelemetryBase):
    """Tests the UasTelemetry interpolate()."""

    def test_single_point(self):
        """Tests handles ranges of points."""
        self.assertTelemetriesEqual(
            self.create_uas_logs([
                (0, 38, -76, 100, 0),
            ]),
            UasTelemetry.interpolate(
                self.create_uas_logs([
                    (0, 38, -76, 100, 0),
                ])))

    def test_position(self):
        """Tests the returned interpolated position."""
        self.assertTelemetriesEqual(
            self.create_uas_logs([
                (0.0, 38, -76, 100, 0),
                (0.1, 39, -75, 105, 1),
                (0.2, 40, -74, 110, 2),
                (0.3, 41, -73, 115, 3),
                (0.4, 42, -72, 120, 4),
                (0.5, 43, -71, 130, 5),
                (0.6, 44, -70, 140, 6),
                (0.7, 45, -69, 150, 7),
            ]),
            UasTelemetry.interpolate(
                self.create_uas_logs([
                    (0.0, 38, -76, 100, 0),
                    (0.2, 40, -74, 110, 2),
                    (0.4, 42, -72, 120, 4),
                    (0.7, 45, -69, 150, 7),
                ])))

    def test_over_step(self):
        """Tests it doesn't interpolate when dt less than step."""
        self.assertTelemetriesEqual(
            self.create_uas_logs([
                (0.0, 38, -76, 100, 0),
                (0.1, 38, -76, 110, 0),
                (0.2, 38, -76, 120, 0),
            ]),
            UasTelemetry.interpolate(
                self.create_uas_logs([
                    (0.0, 38, -76, 100, 0),
                    (0.1, 38, -76, 110, 0),
                    (0.2, 38, -76, 120, 0),
                ])))

    def test_over_max_gap(self):
        """Tests it doesn't interpolate when over the max gap."""
        self.assertTelemetriesEqual(
            self.create_uas_logs([
                (00, 38, -76, 100, 0),
                (10, 38, -76, 110, 0),
            ]),
            UasTelemetry.interpolate(
                self.create_uas_logs([
                    (00, 38, -76, 100, 0),
                    (10, 38, -76, 110, 0),
                ])))


class TestUasTelemetryWaypoints(TestUasTelemetryBase):
    def test_satisfied_waypoints(self):
        """Tests the evaluation of waypoints method."""
        # Create mission config
        gpos = GpsPosition()
        gpos.latitude = 10
        gpos.longitude = 10
        gpos.save()

        waypoints = self.waypoints_from_data([
            (38, -76, 100),
            (39, -77, 200),
            (40, -78, 0),
        ])

        # Only first is valid.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 40, -78, 600, 0),
            (2, 37, -75, 40, 0),
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40),
            WaypointEvaluation(
                id=1, score_ratio=0, closest_for_mission_ft=170),
            WaypointEvaluation(
                id=2, score_ratio=0, closest_for_mission_ft=600)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # First and last are valid.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 40, -78, 600, 0),
            (2, 40, -78, 40, 0),
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40),
            WaypointEvaluation(
                id=1, score_ratio=0, closest_for_mission_ft=170),
            WaypointEvaluation(
                id=2,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Hit all.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 39, -77, 180, 0),
            (2, 40, -78, 40, 0),
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40),
            WaypointEvaluation(
                id=1,
                score_ratio=0.8,
                closest_for_scored_approach_ft=20,
                closest_for_mission_ft=20),
            WaypointEvaluation(
                id=2,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Only hit the first waypoint on run one, hit all on run two.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 40, -78, 600, 0),
            (2, 37, -75, 40, 0),
            # Run two:
            (3, 38, -76, 140, 0),
            (4, 39, -77, 180, 0),
            (5, 40, -78, 40, 0),
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40),
            WaypointEvaluation(
                id=1,
                score_ratio=0.8,
                closest_for_scored_approach_ft=20,
                closest_for_mission_ft=20),
            WaypointEvaluation(
                id=2,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Hit all on run one, only hit the first waypoint on run two.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 39, -77, 180, 0),
            (2, 40, -78, 40, 0),
            # Run two:
            (3, 38, -76, 140, 0),
            (4, 40, -78, 600, 0),
            (5, 37, -75, 40, 0)
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40),
            WaypointEvaluation(
                id=1,
                score_ratio=0.8,
                closest_for_scored_approach_ft=20,
                closest_for_mission_ft=20),
            WaypointEvaluation(
                id=2,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Keep flying after hitting all waypoints.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 39, -77, 180, 0),
            (2, 40, -78, 40, 0),
            (3, 30.1, -78.1, 100, 0),
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40),
            WaypointEvaluation(
                id=1,
                score_ratio=0.8,
                closest_for_scored_approach_ft=20,
                closest_for_mission_ft=20),
            WaypointEvaluation(
                id=2,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=40)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Hit all in first run, but second is higher scoring.
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),
            (1, 39, -77, 180, 0),
            (2, 40, -78, 60, 0),
            # Run two:
            (3, 38, -76, 100, 0),
            (4, 39, -77, 200, 0),
            (5, 40, -78, 110, 0)
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=1,
                closest_for_scored_approach_ft=0,
                closest_for_mission_ft=0),
            WaypointEvaluation(
                id=1,
                score_ratio=1,
                closest_for_scored_approach_ft=0,
                closest_for_mission_ft=0),
            WaypointEvaluation(id=2, score_ratio=0, closest_for_mission_ft=60)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Restart waypoint path in the middle, use path in between points.
        waypoints = self.waypoints_from_data([
            (38, -76, 100),
            (39, -77, 200),
            (40, -78, 0),
        ])
        logs = self.create_uas_logs([
            (0, 38, -76, 140, 0),  # Use
            (1, 39, -77, 180, 0),  # Use
            # Restart:
            (2, 38, -76, 70, 0),
            (3, 39, -77, 150, 0),
            (4, 40, -78, 10, 0),  # Use
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.6,
                closest_for_scored_approach_ft=40,
                closest_for_mission_ft=30),
            WaypointEvaluation(
                id=1,
                score_ratio=0.8,
                closest_for_scored_approach_ft=20,
                closest_for_mission_ft=20),
            WaypointEvaluation(
                id=2,
                score_ratio=0.9,
                closest_for_scored_approach_ft=10,
                closest_for_mission_ft=10)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))

        # Sanity check waypoint scoring with interpolation.
        waypoints = self.waypoints_from_data([
            (38, -76, 70),
            (38, -76, 110),
        ])
        logs = self.create_uas_logs([
            (0, 38, -76, 0, 0),
            (1, 38, -76, 200, 0),
        ])
        expect = [
            WaypointEvaluation(
                id=0,
                score_ratio=0.9,
                closest_for_scored_approach_ft=10,
                closest_for_mission_ft=10),
            WaypointEvaluation(
                id=1,
                score_ratio=0.9,
                closest_for_scored_approach_ft=10,
                closest_for_mission_ft=10)
        ]
        self.assertSatisfiedWaypoints(expect,
                                      UasTelemetry.satisfied_waypoints(
                                          gpos, waypoints, logs))


class TestUasTelemetryKml(TestUasTelemetryBase):
    # String formatter for KML format that expects lon, lat, alt arguments
    coord_format = '<gx:coord>{} {} {}</gx:coord>'

    def test_kml_simple(self):
        coordinates = [
            (0, -76.0, 38.0, 0.0, 0),
            (1, -76.0, 38.0, 10.0, 0),
            (2, -76.0, 38.0, 20.0, 0),
            (3, -76.0, 38.0, 30.0, 0),
            (4, -76.0, 38.0, 100.0, 0),
            (5, -76.0, 38.0, 30.0, 0),
            (6, -76.0, 38.0, 60.0, 0),
        ]
        # Create Coordinates
        start = TakeoffOrLandingEvent(user=self.user, uas_in_air=True)
        start.save()
        start.timestamp = self.now
        start.save()
        for coord in coordinates:
            self.create_log_element(*coord)
        end = TakeoffOrLandingEvent(user=self.user, uas_in_air=False)
        end.save()
        end.timestamp = self.now + datetime.timedelta(seconds=7)
        end.save()

        kml = Kml()
        UasTelemetry.kml(
            user=self.user,
            logs=UasTelemetry.by_user(self.user),
            kml=kml,
            kml_doc=kml.document)
        for coord in coordinates:
            tag = self.coord_format.format(coord[2], coord[1],
                                           units.feet_to_meters(coord[3]))
            self.assertTrue(tag in kml.kml())

    def test_kml_empty(self):
        kml = Kml()
        UasTelemetry.kml(
            user=self.user,
            logs=UasTelemetry.by_user(self.user),
            kml=kml,
            kml_doc=kml.document)

    def test_kml_filter(self):
        coordinates = [
            (0, -76.0, 38.0, 0.0, 0),
            (1, -76.0, 38.0, 10.0, 0),
            (2, -76.0, 38.0, 20.0, 0),
            (3, -76.0, 38.0, 30.0, 0),
            (4, -76.0, 38.0, 100.0, 0),
            (5, -76.0, 38.0, 30.0, 0),
            (6, -76.0, 38.0, 60.0, 0),
        ]
        filtered_out = [
            (7, 0.1, 0.001, 100, 0),
            (8, 0.0, 0.0, 0, 0),
        ]
        # Create Coordinates
        start = TakeoffOrLandingEvent(user=self.user, uas_in_air=True)
        start.save()
        start.timestamp = self.now
        start.save()
        for coord in coordinates:
            self.create_log_element(*coord)
        for coord in filtered_out:
            self.create_log_element(*coord)
        end = TakeoffOrLandingEvent(user=self.user, uas_in_air=False)
        end.save()
        end.timestamp = self.now + datetime.timedelta(seconds=6.5)
        end.save()

        kml = Kml()
        UasTelemetry.kml(
            user=self.user,
            logs=UasTelemetry.by_user(self.user),
            kml=kml,
            kml_doc=kml)

        for filtered in filtered_out:
            tag = self.coord_format.format(filtered[2], filtered[1],
                                           units.feet_to_meters(filtered[3]))
            self.assertTrue(tag not in kml.kml())

        for coord in coordinates:
            tag = self.coord_format.format(coord[2], coord[1],
                                           units.feet_to_meters(coord[3]))
            self.assertTrue(tag in kml.kml())
