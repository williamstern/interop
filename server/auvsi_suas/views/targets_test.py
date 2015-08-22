"""Tests for the missions module."""

import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

login_url = reverse('auvsi_suas:login')
targets_url = reverse('auvsi_suas:targets')


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
