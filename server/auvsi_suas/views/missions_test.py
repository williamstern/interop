"""Tests for the missions module."""

import functools
import io
import json
import zipfile
from auvsi_suas.models import units
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.mission_config import MissionConfig
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from xml.etree import ElementTree

missions_url = reverse('auvsi_suas:missions')
missions_id_url = functools.partial(reverse, 'auvsi_suas:missions_id')
export_url = reverse('auvsi_suas:export_kml')
live_url = reverse('auvsi_suas:live_kml')
update_url = update_url = reverse('auvsi_suas:update_kml')
evaluate_url = functools.partial(reverse, 'auvsi_suas:evaluate')


class TestMissionsViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(missions_url)
        self.assertEqual(403, response.status_code)

        response = self.client.get(missions_id_url(args=[1]))
        self.assertEqual(403, response.status_code)


class TestMissionsViewCommon(TestCase):
    """Common test setup"""

    def setUp(self):
        self.user = User.objects.create_user('user', 'email@example.com',
                                             'normalpass')
        self.user.save()

        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()

    def Login(self):
        self.client.force_login(self.user)

    def LoginSuperuser(self):
        self.client.force_login(self.admin_user)


class TestMissionsViewBasic(TestMissionsViewCommon):
    """Tests the missions view with minimal data."""

    def test_post(self):
        """POST not allowed"""
        self.LoginSuperuser()
        response = self.client.post(missions_url)
        self.assertEqual(405, response.status_code)

    def test_no_missions(self):
        """No missions results in empty list."""
        self.LoginSuperuser()
        response = self.client.get(missions_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], json.loads(response.content))

    def test_incorrect_mission(self):
        self.Login()
        response = self.client.get(missions_id_url(args=[1]))
        self.assertEqual(404, response.status_code)


class TestMissionsViewSampleMission(TestMissionsViewCommon):
    """Tests the missions view with sample mission."""

    fixtures = ['testdata/sample_mission.json']

    def assert_data(self, data):
        self.assertIn('id', data)
        self.assertEqual(3, data['id'])

        self.assertIn('waypoints', data)
        for waypoint in data['waypoints']:
            self.assertIn('latitude', waypoint)
            self.assertIn('longitude', waypoint)
            self.assertIn('altitude', waypoint)

        self.assertEqual(2, len(data['waypoints']))

        self.assertEqual(38.0, data['waypoints'][0]['latitude'])
        self.assertEqual(-76.0, data['waypoints'][0]['longitude'])
        self.assertEqual(30.0, data['waypoints'][0]['altitude'])

        self.assertEqual(38.0, data['waypoints'][1]['latitude'])
        self.assertEqual(-77.0, data['waypoints'][1]['longitude'])
        self.assertEqual(60.0, data['waypoints'][1]['altitude'])

        self.assertIn('searchGridPoints', data)
        self.assertEqual(1, len(data['searchGridPoints']))
        for point in data['searchGridPoints']:
            self.assertIn('latitude', point)
            self.assertIn('longitude', point)

        self.assertEqual(38.0, data['searchGridPoints'][0]['latitude'])
        self.assertEqual(-79.0, data['searchGridPoints'][0]['longitude'])

        self.assertIn('offAxisOdlcPos', data)
        self.assertIn('latitude', data['offAxisOdlcPos'])
        self.assertIn('longitude', data['offAxisOdlcPos'])
        self.assertEqual(38.0, data['offAxisOdlcPos']['latitude'])
        self.assertEqual(-79.0, data['offAxisOdlcPos']['longitude'])

        self.assertIn('emergentLastKnownPos', data)
        self.assertIn('latitude', data['emergentLastKnownPos'])
        self.assertIn('longitude', data['emergentLastKnownPos'])
        self.assertEqual(38.0, data['emergentLastKnownPos']['latitude'])
        self.assertEqual(-79.0, data['emergentLastKnownPos']['longitude'])

        self.assertIn('airDropPos', data)
        self.assertIn('latitude', data['airDropPos'])
        self.assertIn('longitude', data['airDropPos'])
        self.assertEqual(38.0, data['airDropPos']['latitude'])
        self.assertEqual(-79.0, data['airDropPos']['longitude'])

        self.assertIn('stationaryObstacles', data)
        self.assertEqual(2, len(data['stationaryObstacles']))
        for obst in data['stationaryObstacles']:
            self.assertIn('latitude', obst)
            self.assertIn('longitude', obst)
            self.assertIn('radius', obst)
            self.assertIn('height', obst)

        self.assertEqual(38, data['stationaryObstacles'][0]['latitude'])
        self.assertEqual(-76, data['stationaryObstacles'][0]['longitude'])
        self.assertEqual(10, data['stationaryObstacles'][0]['height'])
        self.assertEqual(10, data['stationaryObstacles'][0]['radius'])

    def test_get(self):
        """Response JSON is properly formatted."""
        self.Login()
        response = self.client.get(missions_id_url(args=[3]))
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assert_data(data)


class TestGenerateKMLCommon(TestCase):
    """Tests the generateKML view."""

    # String formatter for KML format that expects lon, lat, alt arguments
    coord_format = '<gx:coord>{} {} {}</gx:coord>'

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
            'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()

    def validate_kml(self, kml_data, folders, users, coordinates):
        kml_data = kml_data.decode('utf-8')
        ElementTree.fromstring(kml_data)
        for folder in folders:
            tag = '<name>{}</name>'.format(folder)
            self.assertTrue(tag in kml_data)

        for user in users:
            tag = '<name>{}</name>'.format(user)
            self.assertIn(tag, kml_data)

        for coord in coordinates:
            coord_str = self.coord_format.format(coord[0], coord[1], coord[2])
            self.assertIn(coord_str, kml_data)


class TestGenerateKMLNoFixture(TestGenerateKMLCommon):
    """Tests the generateKML view."""

    def __init__(self, *args, **kwargs):
        super(TestGenerateKMLNoFixture, self).__init__(*args, **kwargs)
        self.folders = ['Missions']
        self.users = []
        self.coordinates = []

    def test_generateKML_not_logged_in(self):
        """Tests the generate KML method."""
        response = self.client.get(export_url)
        self.assertEqual(403, response.status_code)

    def test_generateKML_nonadmin(self):
        """Tests the generate KML method."""
        self.client.force_login(self.nonadmin_user)
        response = self.client.get(export_url)
        self.assertEqual(403, response.status_code)

    def test_generateKML(self):
        """Tests the generate KML method."""
        self.client.force_login(self.admin_user)
        response = self.client.get(export_url)
        self.assertEqual(200, response.status_code)
        kml_data = response.content
        self.validate_kml(kml_data, self.folders, self.users, self.coordinates)


class TestGenerateKMLWithFixture(TestGenerateKMLCommon):
    """Tests the generateKML view."""
    fixtures = ['testdata/sample_mission.json']

    def __init__(self, *args, **kwargs):
        super(TestGenerateKMLWithFixture, self).__init__(*args, **kwargs)
        self.folders = ['Flights', 'Missions']
        self.users = ['user0', 'user1']
        self.coordinates = [(lat, lon, units.feet_to_meters(alt))
                            for lat, lon, alt in [
                                (-76.0, 38.0, 0.0),
                                (-76.0, 38.0, 10.0),
                                (-76.0, 38.0, 20.0),
                                (-76.0, 38.0, 30.0),
                                (-76.0, 38.0, 100.0),
                                (-76.0, 38.0, 30.0),
                                (-77.0, 38.0, 60.0),
                            ]]

    def test_generateKML_not_logged_in(self):
        """Tests the generate KML method."""
        response = self.client.get(export_url)
        self.assertEqual(403, response.status_code)

    def test_generateKML_nonadmin(self):
        """Tests the generate KML method."""
        self.client.force_login(self.nonadmin_user)
        response = self.client.get(export_url)
        self.assertEqual(403, response.status_code)

    def test_generateKML(self):
        """Tests the generate KML method."""
        self.client.force_login(self.admin_user)
        response = self.client.get(export_url)
        self.assertEqual(200, response.status_code)

        kml_data = response.content
        self.validate_kml(kml_data, self.folders, self.users, self.coordinates)


class TestGenerateLiveKMLCommon(TestCase):
    """Tests the generateKML view."""

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
            'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()


class TestGenerateLiveKMLNoFixture(TestGenerateLiveKMLCommon):
    def setUp(self):
        """Setup a single mission to test live kml with."""
        super(TestGenerateLiveKMLNoFixture, self).setUp()

        pos = GpsPosition()
        pos.latitude = 10
        pos.longitude = 10
        pos.save()

        config = MissionConfig()
        config.home_pos = pos
        config.emergent_last_known_pos = pos
        config.off_axis_odlc_pos = pos
        config.air_drop_pos = pos
        config.save()
        self.config = config

    def test_generate_live_kml_not_logged_in(self):
        """Tests the generate KML method."""
        response = self.client.get(live_url)
        self.assertEqual(403, response.status_code)

    def test_generate_live_kml(self):
        """Tests the generate KML method."""
        self.client.force_login(self.admin_user)
        response = self.client.get(live_url)
        self.assertEqual(200, response.status_code)

    def test_generate_live_kml_nonadmin(self):
        """Tests the generate KML method."""
        self.client.force_login(self.nonadmin_user)
        response = self.client.get(live_url)
        self.assertEqual(403, response.status_code)

    def test_generate_live_kml_update_no_session_id(self):
        """Tests the generate KML method."""
        response = self.client.get(update_url)
        self.assertEqual(403, response.status_code)

    def test_generate_live_kml_update_bad_session_id(self):
        """Tests the generate KML method."""
        bad_id = '360l8fjqnvzbviy590gmjeltma9fx26f'
        response = self.client.get(update_url, {'sessionid': bad_id})
        self.assertEqual(403, response.status_code)

    def test_generate_live_kml_update_nonadmin(self):
        """Tests the generate KML method."""
        self.client.force_login(self.nonadmin_user)
        response = self.client.get(update_url,
                                   {'sessionid': self.get_session_id()})
        self.assertEqual(403, response.status_code)

    def test_generate_live_kml_update(self):
        """Tests the generate KML method."""
        self.client.force_login(self.admin_user)
        response = self.client.get(update_url,
                                   {'sessionid': self.get_session_id()})
        self.assertEqual(200, response.status_code)

    def get_session_id(self):
        for item in self.client.cookies.items():
            morsel = item[1]
            if morsel.key == 'sessionid':
                return morsel.value


class TestGenerateLiveKMLWithFixture(TestGenerateLiveKMLCommon):
    """Tests the generateKML view."""
    fixtures = ['testdata/sample_mission.json']

    def test_generate_live_kml(self):
        """Tests the generate KML method."""
        self.client.force_login(self.admin_user)

        response = self.client.get(live_url)
        self.assertEqual(200, response.status_code)

        response = self.client.get(update_url)
        self.assertEqual(200, response.status_code)


class TestEvaluateTeams(TestCase):
    """Tests the evaluate_teams view."""

    fixtures = ['testdata/sample_mission.json']

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
            'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()
        self.nonadmin_client = Client()
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()
        self.admin_client = Client()

    def test_evaluate_teams_nonadmin(self):
        """Tests that you can only access data as admin."""
        self.client.force_login(self.nonadmin_user)
        response = self.client.get(evaluate_url(args=[1]))
        self.assertEqual(403, response.status_code)

    def test_invalid_mission(self):
        """Tests that an invalid mission ID results in error."""
        self.client.force_login(self.nonadmin_user)
        response = self.client.get(evaluate_url(args=[1000]))
        self.assertGreaterEqual(response.status_code, 400)

    def load_json(self, response):
        """Gets the json data out of the response's zip archive."""
        zip_io = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_io, 'r') as zip_file:
            return json.loads(zip_file.read('/evaluate_teams/all.json'))

    def load_csv(self, response):
        """Gets the CSV data out of the response's zip archive."""
        zip_io = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_io, 'r') as zip_file:
            return zip_file.read('/evaluate_teams/all.csv').decode('utf-8')

    def test_evaluate_teams(self):
        """Tests the eval Json method."""
        self.client.force_login(self.admin_user)
        response = self.client.get(evaluate_url(args=[3]))
        self.assertEqual(response.status_code, 200)
        data = self.load_json(response)
        self.assertIn('teams', data)
        teams = data['teams']
        self.assertEqual(len(teams), 2)
        self.assertEqual('user0', teams[0]['team'])
        self.assertEqual('user1', teams[1]['team'])
        self.assertIn('waypoints', teams[0]['feedback'])

    def test_evaluate_teams_specific_team(self):
        """Tests the eval Json method on a specific team."""
        self.client.force_login(self.admin_user)
        response = self.client.get(evaluate_url(args=[3]), {'team': 53})
        self.assertEqual(response.status_code, 200)
        data = self.load_json(response)
        self.assertIn('teams', data)
        teams = data['teams']
        self.assertEqual(len(teams), 1)
        self.assertEqual('user0', teams[0]['team'])

    def test_evaluate_teams_csv(self):
        """Tests the CSV method."""
        self.client.force_login(self.admin_user)
        response = self.client.get(evaluate_url(args=[3]))
        self.assertEqual(response.status_code, 200)
        csv_data = self.load_csv(response)
        self.assertEqual(len(csv_data.split('\n')), 4)
        self.assertIn('team', csv_data)
        self.assertIn('waypoints', csv_data)
        self.assertIn('user0', csv_data)
        self.assertIn('user1', csv_data)
