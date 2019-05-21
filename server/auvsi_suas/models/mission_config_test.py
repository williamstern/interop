"""Tests for the mission_config module."""

from auvsi_suas.models.mission_config import MissionConfig
from django.test import TestCase


class TestMissionConfigModelSampleMission(TestCase):

    fixtures = ['testdata/sample_mission.json']

    def test_str(self):
        for mission in MissionConfig.objects.all():
            self.assertNotEqual(str(mission), '')

    def test_clean(self):
        """Test model validation."""
        for mission in MissionConfig.objects.all():
            mission.full_clean()
