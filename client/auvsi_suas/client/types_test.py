import unittest

from auvsi_suas.client.types import Odlc


class TestOdlc(unittest.TestCase):
    """Tests the Odlc model for validation and serialization."""

    def test_valid(self):
        """Test valid inputs."""
        Odlc(
            id=1,
            user=2,
            type='standard',
            latitude=10,
            longitude=-10,
            orientation='n',
            shape='circle',
            background_color='white',
            alphanumeric='a',
            alphanumeric_color='black')

        Odlc(
            type='off_axis',
            latitude=10,
            longitude=-10,
            orientation='n',
            shape='circle',
            background_color='white',
            alphanumeric='a',
            alphanumeric_color='black')

        Odlc(
            type='emergent',
            latitude=10,
            longitude=-10,
            description='Fireman putting out a fire.')

        Odlc(type='standard', latitude=10, longitude=-10, autonomous=True)

    def test_invalid(self):
        """Test invalid inputs."""
        # Bad latitude.
        with self.assertRaises(ValueError):
            Odlc(
                type='emergent',
                latitude='a',
                longitude=-10,
                description='Firefighter')

        with self.assertRaises(ValueError):
            Odlc(
                type='emergent',
                latitude=10,
                longitude='a',
                description='Firefighter')

    def test_serialize(self):
        """Test serialization."""
        o = Odlc(
            id=1,
            user=2,
            type='standard',
            latitude=10,
            longitude=-10,
            orientation='n',
            shape='circle',
            background_color='white',
            alphanumeric='a',
            alphanumeric_color='black',
            autonomous=True,
            actionable_override=True,
            team_id='testuser')
        s = o.serialize()

        self.assertEqual(13, len(s))
        self.assertEqual(1, s['id'])
        self.assertEqual(2, s['user'])
        self.assertEqual('standard', s['type'])
        self.assertEqual(10, s['latitude'])
        self.assertEqual(-10, s['longitude'])
        self.assertEqual('n', s['orientation'])
        self.assertEqual('circle', s['shape'])
        self.assertEqual('white', s['background_color'])
        self.assertEqual('a', s['alphanumeric'])
        self.assertEqual('black', s['alphanumeric_color'])
        self.assertEqual(True, s['autonomous'])
        self.assertEqual(True, s['actionable_override'])
        self.assertEqual('testuser', s['team_id'])

    def test_deserialize(self):
        """Test deserialization."""
        o = Odlc.deserialize({
            'type': 'standard',
            'latitude': '10',
            'longitude': -10,
            'orientation': 'n',
            'shape': 'circle',
            'background_color': 'white',
            'alphanumeric': 'a',
            'alphanumeric_color': 'black',
            'autonomous': True,
            'actionable_override': True,
            'team_id': 'testuser'
        })

        self.assertEqual('standard', o.type)
        self.assertEqual(10, o.latitude)
        self.assertEqual(-10, o.longitude)
        self.assertEqual('n', o.orientation)
        self.assertEqual('circle', o.shape)
        self.assertEqual('white', o.background_color)
        self.assertEqual('a', o.alphanumeric)
        self.assertEqual('black', o.alphanumeric_color)
        self.assertEqual(True, o.autonomous)
        self.assertEqual(True, o.actionable_override)
        self.assertEqual('testuser', o.team_id)

        o = Odlc.deserialize({'type': 'emergent'})

        self.assertEqual('emergent', o.type)
