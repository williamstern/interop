"""Tests for the missions module."""

import functools
import json
from auvsi_suas.models import GpsPosition, Target, TargetType, Color, Shape, Orientation
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

login_url = reverse('auvsi_suas:login')
targets_url = reverse('auvsi_suas:targets')
targets_id_url = functools.partial(reverse, 'auvsi_suas:targets_id')


class TestTargetsLoggedOut(TestCase):
    """Tests logged out targets."""

    def test_not_authenticated(self):
        """Unauthenticated requests should fail."""
        target = {'type': 'standard', 'latitude': 38, 'longitude': -76, }

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(403, response.status_code)


class TestPostTarget(TestCase):
    """Tests POSTing the targets view."""

    def setUp(self):
        """Creates user and logs in."""
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')

        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(200, response.status_code)

    def test_get(self):
        """GET not yet supported."""
        response = self.client.get(targets_url)
        self.assertEqual(405, response.status_code)

    def test_complete(self):
        """Send complete target with all fields."""
        target = {
            'type': 'standard',
            'latitude': 38,
            'longitude': -76,
            'orientation': 'n',
            'shape': 'square',
            'background_color': 'white',
            'alphanumeric': 'ABC',
            'alphanumeric_color': 'black',
            'description': 'Best target',
        }

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

        # Check that returned target matches
        created = json.loads(response.content)

        self.assertEqual(target['type'], created['type'])
        self.assertEqual(target['latitude'], created['latitude'])
        self.assertEqual(target['longitude'], created['longitude'])
        self.assertEqual(target['orientation'], created['orientation'])
        self.assertEqual(target['shape'], created['shape'])
        self.assertEqual(target['background_color'],
                         created['background_color'])
        self.assertEqual(target['alphanumeric'], created['alphanumeric'])
        self.assertEqual(target['alphanumeric_color'],
                         created['alphanumeric_color'])
        self.assertEqual(target['description'], created['description'])

        # It also contains 'user' and 'id' fields.
        self.assertIn('id', created)
        self.assertIn('user', created)

    def test_minimal(self):
        """Send target minimal fields."""
        target = {'type': 'standard'}

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

        # Check that returned target matches
        created = json.loads(response.content)

        self.assertEqual(target['type'], created['type'])
        self.assertEqual(None, created['latitude'])
        self.assertEqual(None, created['longitude'])
        self.assertEqual(None, created['orientation'])
        self.assertEqual(None, created['shape'])
        self.assertEqual(None, created['background_color'])
        self.assertEqual(None, created['alphanumeric'])
        self.assertEqual(None, created['alphanumeric_color'])
        self.assertEqual(None, created['description'])

        # It also contains 'user' and 'id' fields.
        self.assertIn('id', created)
        self.assertIn('user', created)

    def test_none(self):
        """Send target with None fields has no effect."""
        target = {'type': 'standard', 'latitude': None, 'shape': None}

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

        # Check that returned target matches
        created = json.loads(response.content)

        self.assertEqual(target['type'], created['type'])
        self.assertEqual(None, created['latitude'])
        self.assertEqual(None, created['shape'])

    def test_missing_type(self):
        """Target type required."""
        target = {
            'latitude': 38,
            'longitude': -76,
            'orientation': 'N',
            'shape': 'square',
            'background_color': 'white',
            'alphanumeric': 'ABC',
            'alphanumeric_color': 'black',
            'description': 'Best target',
        }

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_missing_latitude(self):
        """Target latitude required if longitude specified."""
        target = {'type': 'standard', 'longitude': -76}

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_missing_longitude(self):
        """Target longitude required if latitude specified."""
        target = {'type': 'standard', 'latitude': 38}

        response = self.client.post(targets_url,
                                    data=json.dumps(target),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_invalid_type(self):
        """Send bad target type."""
        bad = ['foo', 'standard nonsense', 42]

        for b in bad:
            target = {'type': b, 'latitude': 38, 'longitude': -76}

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)

    def test_invalid_latitude(self):
        """Send bad target latitude."""
        bad = ['string', 120, -120]

        for b in bad:
            target = {'type': 'standard', 'latitude': b, 'longitude': -76}

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)

    def test_invalid_longitude(self):
        """Send bad target longitude."""
        bad = ['string', 200, -200]

        for b in bad:
            target = {'type': 'standard', 'latitude': 38, 'longitude': b}

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)

    def test_invalid_shape(self):
        """Send bad target shape."""
        bad = ['square circle', 'dodecahedron', 42]

        for b in bad:
            target = {
                'type': 'standard',
                'latitude': 38,
                'longitude': -76,
                'shape': b,
            }

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)

    def test_invalid_background_color(self):
        """Send bad target background color."""
        bad = ['white black', 'mahogany', 42]

        for b in bad:
            target = {
                'type': 'standard',
                'latitude': 38,
                'longitude': -76,
                'background_color': b,
            }

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)

    def test_invalid_alphanumeric_color(self):
        """Send bad target alphanumeric color."""
        bad = ['white black', 'mahogany', 42]

        for b in bad:
            target = {
                'type': 'standard',
                'latitude': 38,
                'longitude': -76,
                'alphanumeric_color': b,
            }

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)

    def test_invalid_orientation(self):
        """Send bad target orientation."""
        bad = ['NNE', 'north', 42]

        for b in bad:
            target = {
                'type': 'standard',
                'latitude': 38,
                'longitude': -76,
                'orientation': b,
            }

            response = self.client.post(targets_url,
                                        data=json.dumps(target),
                                        content_type='application/json')
            self.assertEqual(400, response.status_code)


class TestTargetsIdLoggedOut(TestCase):
    """Tests logged out targets_id."""

    def test_not_authenticated(self):
        """Unauthenticated requests should fail."""
        response = self.client.get(targets_id_url(args=[1]))
        self.assertEqual(403, response.status_code)


class TestTargetId(TestCase):
    """Tests GET/PUT specific targets."""

    def setUp(self):
        """Creates user and logs in."""
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')

        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(200, response.status_code)

    def test_get_nonexistent(self):
        """Test GETting a target that doesn't exist."""
        response = self.client.get(targets_id_url(args=[999]))
        self.assertEqual(404, response.status_code)

    def test_get_other_user(self):
        """Test GETting a target owned by a different user."""
        user2 = User.objects.create_user('testuser2', 'testemail@x.com',
                                         'testpass')
        t = Target(user=user2, target_type=TargetType.standard)
        t.save()

        response = self.client.get(targets_id_url(args=[t.pk]))
        self.assertEqual(403, response.status_code)

    def test_get_own(self):
        """Test GETting a target owned by the correct user."""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

        response = self.client.get(targets_id_url(args=[t.pk]))
        self.assertEqual(200, response.status_code)

        self.assertEqual(t.json(), json.loads(response.content))

    def test_put_append(self):
        """PUT sets a new field that wasn't set before."""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

        data = {'description': 'Hello'}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(200, response.status_code)

        t.refresh_from_db()
        self.assertEqual('Hello', t.description)

        # Response also matches
        self.assertEqual(t.json(), json.loads(response.content))

    def test_put_one(self):
        """PUT update one field without affecting others."""
        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(
            user=self.user,
            target_type=TargetType.standard,
            location=l,
            orientation=Orientation.s,
            shape=Shape.square,
            background_color=Color.white,
            alphanumeric='ABC',
            alphanumeric_color=Color.black,
            description='Test target')
        t.save()

        data = {'shape': 'circle'}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(200, response.status_code)

        t.refresh_from_db()
        t.location.refresh_from_db()
        self.assertEqual(self.user, t.user)
        self.assertEqual(TargetType.standard, t.target_type)
        self.assertEqual(38, t.location.latitude)
        self.assertEqual(-76, t.location.longitude)
        self.assertEqual(Orientation.s, t.orientation)
        self.assertEqual(Shape.circle, t.shape)
        self.assertEqual(Color.white, t.background_color)
        self.assertEqual('ABC', t.alphanumeric)
        self.assertEqual(Color.black, t.alphanumeric_color)
        self.assertEqual('Test target', t.description)

    def test_put_clear_shape(self):
        """PUT clear a field with None."""
        t = Target(user=self.user,
                   target_type=TargetType.standard,
                   shape=Shape.square)
        t.save()

        data = {'shape': None}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(200, response.status_code)

        t.refresh_from_db()
        self.assertEqual(None, t.shape)

    def test_put_clear_type(self):
        """PUT type may not be cleared."""
        t = Target(user=self.user,
                   target_type=TargetType.standard,
                   shape=Shape.square)
        t.save()

        data = {'type': None}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(400, response.status_code)

    def test_put_location(self):
        """PUT new location"""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

        data = {'latitude': 38, 'longitude': -76}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(200, response.status_code)

        t.refresh_from_db()
        self.assertEqual(38, t.location.latitude)
        self.assertEqual(-76, t.location.longitude)

    def test_put_location_missing_one(self):
        """PUTting new location requires both latitude and longitude."""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

        data = {'latitude': 38}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(400, response.status_code)

    def test_put_update_location(self):
        """PUT updating location only requires one of lat/lon."""
        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(user=self.user, target_type=TargetType.standard, location=l)
        t.save()

        data = {'latitude': 39}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(200, response.status_code)

        t.refresh_from_db()
        t.location.refresh_from_db()
        self.assertEqual(39, t.location.latitude)
        self.assertEqual(-76, t.location.longitude)

    def test_put_clear_location(self):
        """PUT clear location by clearing lat and lon."""
        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(user=self.user, target_type=TargetType.standard, location=l)
        t.save()

        data = {'latitude': None, 'longitude': None}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(200, response.status_code)

        t.refresh_from_db()
        self.assertEqual(None, t.location)

    def test_put_partial_clear_location(self):
        """PUT can't clear location with only one of lat/lon."""
        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(user=self.user, target_type=TargetType.standard, location=l)
        t.save()

        data = {'latitude': None}

        response = self.client.put(targets_id_url(args=[t.pk]),
                                   data=json.dumps(data))
        self.assertEqual(400, response.status_code)
