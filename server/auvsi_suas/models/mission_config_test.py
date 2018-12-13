"""Tests for the mission_config module."""

from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.patches.simplekml_patch import Kml
from django.test import TestCase


class TestMissionConfigModelSampleMission(TestCase):

    fixtures = ['testdata/sample_mission.json']

    def test_toKML(self):
        """Test Generation of kml for all mission data"""
        kml = Kml()
        MissionConfig.kml_all(kml, kml.document)
        data = kml.kml()
        names = [
            'Off Axis',
            'Home',
            'Air Drop',
            'Emergent LKP',
            'Search Area',
            'Waypoints',
        ]
        for name in names:
            tag = '<name>{}</name>'.format(name)
            err = 'tag "{}" not found in {}'.format(tag, data)
            self.assertIn(tag, data, err)
