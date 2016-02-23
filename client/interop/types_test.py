import unittest

from . import Telemetry, StationaryObstacle, MovingObstacle, Target


class TestTelemetry(unittest.TestCase):
    """Test the Telemetry object. There is very little to see here."""

    def test_valid(self):
        """Test valid inputs"""
        # No exceptions
        Telemetry(latitude=38, longitude=-76, altitude_msl=100, uas_heading=90)

    def test_invalid(self):
        """Test invalid inputs"""
        # Bad latitude
        with self.assertRaises(ValueError):
            Telemetry(latitude='a',
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading=90)
        # Bad longitude
        with self.assertRaises(ValueError):
            Telemetry(latitude=38,
                      longitude='a',
                      altitude_msl=100,
                      uas_heading=90)
        # Bad altitude
        with self.assertRaises(ValueError):
            Telemetry(latitude=38,
                      longitude=-76,
                      altitude_msl='a',
                      uas_heading=90)
        # Bad heading
        with self.assertRaises(ValueError):
            Telemetry(latitude=38,
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading='a')

    def test_serialize(self):
        """Test serialization."""
        t = Telemetry(latitude=38,
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading=90)
        s = t.serialize()

        self.assertEqual(4, len(s))
        self.assertEqual(38, s['latitude'])
        self.assertEqual(-76, s['longitude'])
        self.assertEqual(100, s['altitude_msl'])
        self.assertEqual(90, s['uas_heading'])

    def test_deserialize(self):
        """Test deserialization."""
        t = Telemetry.deserialize({
            'latitude': 38,
            'longitude': '-76',
            'altitude_msl': 100,
            'uas_heading': 90
        })

        self.assertEqual(38, t.latitude)
        self.assertEqual(-76, t.longitude)
        self.assertEqual(100, t.altitude_msl)
        self.assertEqual(90, t.uas_heading)


class TestStationaryObstacle(unittest.TestCase):
    """Test the StationaryObstacle object. There is very little to see here."""

    def test_valid(self):
        """Test valid inputs"""
        # No exceptions
        StationaryObstacle(latitude=38,
                           longitude=-76,
                           cylinder_radius=100,
                           cylinder_height=200)

    def test_invalid(self):
        """Test invalid inputs"""
        # Bad latitude
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude='a',
                               longitude=-76,
                               cylinder_radius=100,
                               cylinder_height=200)
        # Bad longitude
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude='a',
                               cylinder_radius=100,
                               cylinder_height=200)
        # Bad radius
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude=-76,
                               cylinder_radius='a',
                               cylinder_height=200)
        # Bad height
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude=-76,
                               cylinder_radius=100,
                               cylinder_height='a')

    def test_serialize(self):
        """Test serialization."""
        o = StationaryObstacle(latitude=38,
                               longitude=-76,
                               cylinder_radius=100,
                               cylinder_height=200)
        s = o.serialize()

        self.assertEqual(4, len(s))
        self.assertEqual(38, s['latitude'])
        self.assertEqual(-76, s['longitude'])
        self.assertEqual(100, s['cylinder_radius'])
        self.assertEqual(200, s['cylinder_height'])

    def test_deserialize(self):
        """Test deserialization."""
        o = StationaryObstacle.deserialize({
            'latitude': '38',
            'longitude': -76,
            'cylinder_radius': 100,
            'cylinder_height': 200
        })

        self.assertEqual(38, o.latitude)
        self.assertEqual(-76, o.longitude)
        self.assertEqual(100, o.cylinder_radius)
        self.assertEqual(200, o.cylinder_height)


class TestMovingObstacle(unittest.TestCase):
    """Test the MovingObstacle object. There is very little to see here."""

    def test_valid(self):
        """Test valid inputs"""
        # No exceptions
        MovingObstacle(latitude=38,
                       longitude=-76,
                       altitude_msl=100,
                       sphere_radius=200)

    def test_invalid(self):
        """Test invalid inputs"""
        # Bad latitude
        with self.assertRaises(ValueError):
            MovingObstacle(latitude='a',
                           longitude=-76,
                           altitude_msl=100,
                           sphere_radius=200)
        # Bad longitude
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=38,
                           longitude='a',
                           altitude_msl=100,
                           sphere_radius=200)
        # Bad altitude
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=38,
                           longitude=-76,
                           altitude_msl='a',
                           sphere_radius=-200)
        # Bad radius
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=38,
                           longitude=-76,
                           altitude_msl=100,
                           sphere_radius='a')

    def test_serialize(self):
        """Test serialization."""
        o = MovingObstacle(latitude=38,
                           longitude=-76,
                           altitude_msl=100,
                           sphere_radius=200)
        s = o.serialize()

        self.assertEqual(4, len(s))
        self.assertEqual(38, s['latitude'])
        self.assertEqual(-76, s['longitude'])
        self.assertEqual(100, s['altitude_msl'])
        self.assertEqual(200, s['sphere_radius'])

    def test_deserialize(self):
        """Test deserialization."""
        o = MovingObstacle.deserialize({
            'latitude': 38,
            'longitude': -76,
            'altitude_msl': 100,
            'sphere_radius': 200
        })

        self.assertEqual(38, o.latitude)
        self.assertEqual(-76, o.longitude)
        self.assertEqual(100, o.altitude_msl)
        self.assertEqual(200, o.sphere_radius)


class TestTarget(unittest.TestCase):
    """Tests the Target model for validation and serialization."""

    def test_valid(self):
        """Test valid inputs."""
        Target(id=1,
               user=2,
               type='standard',
               latitude=10,
               longitude=-10,
               orientation='n',
               shape='circle',
               background_color='white',
               alphanumeric='a',
               alphanumeric_color='black')

        Target(type='qrc',
               latitude=10,
               longitude=-10,
               description='http://test.com')

        Target(type='off_axis',
               latitude=10,
               longitude=-10,
               orientation='n',
               shape='circle',
               background_color='white',
               alphanumeric='a',
               alphanumeric_color='black')

        Target(type='emergent',
               latitude=10,
               longitude=-10,
               description='Fireman putting out a fire.')

    def test_invalid(self):
        """Test invalid inputs."""
        # Bad latitude.
        with self.assertRaises(ValueError):
            Target(type='qrc',
                   latitude='a',
                   longitude=-10,
                   description='http://test.com')

        with self.assertRaises(ValueError):
            Target(type='qrc',
                   latitude=10,
                   longitude='a',
                   description='http://test.com')

    def test_serialize(self):
        """Test serialization."""
        o = Target(id=1,
                   user=2,
                   type='standard',
                   latitude=10,
                   longitude=-10,
                   orientation='n',
                   shape='circle',
                   background_color='white',
                   alphanumeric='a',
                   alphanumeric_color='black')
        s = o.serialize()

        self.assertEqual(10, len(s))
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

    def test_deserialize(self):
        """Test deserialization."""
        o = Target.deserialize({
            'type': 'standard',
            'latitude': '10',
            'longitude': -10,
            'orientation': 'n',
            'shape': 'circle',
            'background_color': 'white',
            'alphanumeric': 'a',
            'alphanumeric_color': 'black'
        })

        self.assertEqual('standard', o.type)
        self.assertEqual(10, o.latitude)
        self.assertEqual(-10, o.longitude)
        self.assertEqual('n', o.orientation)
        self.assertEqual('circle', o.shape)
        self.assertEqual('white', o.background_color)
        self.assertEqual('a', o.alphanumeric)
        self.assertEqual('black', o.alphanumeric_color)

        o = Target.deserialize({'type': 'qrc'})

        self.assertEqual('qrc', o.type)
