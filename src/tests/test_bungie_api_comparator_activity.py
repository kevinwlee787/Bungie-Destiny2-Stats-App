import sys
import pathlib

sys.path.insert(1, str(pathlib.Path().absolute()) + '\\')

from src.bungie_api.bungieD2_api import *
import unittest

class TestCmpActivity(unittest.TestCase):

    def test_year(self):
        act1 = {'period' : '2021-09-11T05:15:44Z' }
        act2 = {'period' : '2020-09-11T05:15:44Z' }
        self.assertTrue(comparator_activity(act1, act2))
        self.assertFalse(comparator_activity(act2, act1))

    def test_month(self):
        act1 = {'period' : '2021-10-11T05:15:44Z' }
        act2 = {'period' : '2021-09-11T05:15:44Z' }
        self.assertTrue(comparator_activity(act1, act2))
        self.assertFalse(comparator_activity(act2, act1))

    def test_day(self):
        act1 = {'period' : '2021-10-11T05:15:44Z' }
        act2 = {'period' : '2021-10-10T05:15:44Z' }
        self.assertTrue(comparator_activity(act1, act2))
        self.assertFalse(comparator_activity(act2, act1))

    def test_hour(self):
        act1 = {'period' : '2021-10-11T05:15:44Z' }
        act2 = {'period' : '2021-10-11T04:15:44Z' }
        self.assertTrue(comparator_activity(act1, act2))
        self.assertFalse(comparator_activity(act2, act1))

    def test_minute(self):
        act1 = {'period' : '2021-10-11T05:15:44Z' }
        act2 = {'period' : '2021-10-11T05:14:44Z' }
        self.assertTrue(comparator_activity(act1, act2))
        self.assertFalse(comparator_activity(act2, act1))

    def test_realistic(self):
        act1 = {'period' : '2021-10-11T05:15:44Z' }
        act2 = {'period' : '2021-09-11T05:07:21Z' }
        self.assertTrue(comparator_activity(act1, act2))
        self.assertFalse(comparator_activity(act2, act1))

    def test_whole_list(self):
        """ This tests real api data recieved from Bungie! """
        gamertag = 'Charmander787#5161'
        player = get_player(gamertag)
        profile = get_profile(player, components = ['1100', '200'])
        characters = profile['characters']['data']
        
        count = 100
        hist = get_activity_history(player, next(iter(characters.keys())), count, modes = ['84'])

        for i in range(len(hist) - 1):
            self.assertTrue(comparator_activity(hist[i], hist[i + 1]))
            self.assertFalse(comparator_activity(hist[i + 1], hist[i]))

        
if __name__ == '__main__':
    unittest.main()