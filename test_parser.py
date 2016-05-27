import unittest
import function_parser as p
from class_parser import ScheduleParser, DEFAULT_TZ, VALID_HOURS, VALID_DAYS


class ScheduleParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = ScheduleParser()

    def test_parses_schedule(self):
        s = self.parser.parse('off=(M-F,19);on=(M-F,7);tz=pst')
        self.assertEquals(
            [{ 'days': ['M', 'T', 'W', 'H', 'F'], 'hour': 19 }],
            s['off']
        )
        self.assertEquals(
            [{ 'days': ['M', 'T', 'W', 'H', 'F'], 'hour': 7 }],
            s['on']
        )
        self.assertEquals('pst', s['tz'])

    def test_parses_default_tz(self):
        s = self.parser.parse('off=(M-F,19);on=(M-F,7)')
        self.assertEquals(
            [{ 'days': ['M', 'T', 'W', 'H', 'F'], 'hour': 19 }],
            s['off']
        )
        self.assertEquals(
            [{ 'days': ['M', 'T', 'W', 'H', 'F'], 'hour': 7 }],
            s['on']
        )
        self.assertEquals(DEFAULT_TZ, s['tz'])

    def test_parses_multiple_hours(self):
        s = self.parser.parse('off=[(M-F,19),(S,9)];on=[(M-F,7),(S,15)];tz=pst')
        self.assertEquals(
            [
                { 'days': ['M', 'T', 'W', 'H', 'F'], 'hour': 19 },
                { 'days': ['S'], 'hour': 9 }
            ],
            s['off']
        )
        self.assertEquals(
            [
                { 'days': ['M', 'T', 'W', 'H', 'F'], 'hour': 7 },
                { 'days': ['S'], 'hour': 15 }
            ],
            s['on']
        )
        self.assertEquals('pst', s['tz'])

    def test_invalid_hour(self):
        s = self.parser.parse('off=(M-F,asdf);on=(M-F,asdf)')
        self.assertEquals(None, s)

    def test_invalid_day(self):
        s = self.parser.parse('off=(asdf,19);on=(asdf,7)')
        self.assertEquals(None, s)

    def test_valid_hour_range(self):
        self.assertEquals(True, self.parser.is_valid_hour_range(0))
        self.assertEquals(True, self.parser.is_valid_hour_range(12))
        self.assertEquals(True, self.parser.is_valid_hour_range(23))
        self.assertEquals(False, self.parser.is_valid_hour_range(24))
        self.assertEquals(False, self.parser.is_valid_hour_range(99))

    def test_valid_day(self):
        for d in VALID_DAYS:
            self.assertEquals(True, self.parser.is_valid_day(d))
        self.assertEquals(False, self.parser.is_valid_day("x"))


class ParserTest(unittest.TestCase):

    def test_valid_day_range(self):
        self.assertTrue(p.valid_day_range("M-F"))
        self.assertTrue(p.valid_day_range("W-S"))
        self.assertTrue(p.valid_day_range("F-T"))
        self.assertFalse(p.valid_day_range("F-F"))
        self.assertTrue(p.valid_day_range("M"))
        self.assertTrue(p.valid_day_range("U"))
        self.assertFalse(p.valid_day_range("Z"))

    def test_parse_time(self):
        self.assertEquals([{ "days": "M", "hour": 9 }], p.parse_time("M", 9))
        self.assertEquals([{ "days": "W", "hour": 19 }], p.parse_time("W", 19))
        self.assertEquals([], p.parse_time("W", 99))
        self.assertEquals([], p.parse_time("Z", 9))
        self.assertEquals([], p.parse_time("Z", 99))
        self.assertEquals(
            [
                { "days": "M", "hour": 9 },
                { "days": "T", "hour": 9 },
                { "days": "W", "hour": 9 },
                { "days": "H", "hour": 9 },
                { "days": "F", "hour": 9 }
            ],
            p.parse_time("M-F", 9)
        )
        self.assertEquals(
            [
                { "days": "F", "hour": 9 },
                { "days": "S", "hour": 9 },
                { "days": "U", "hour": 9 },
                { "days": "M", "hour": 9 },
                { "days": "T", "hour": 9 }
            ],
            p.parse_time("F-T", 9)
        )
        self.assertEquals([], p.parse_time("F-T", 99))
        self.assertEquals([], p.parse_time("F-F", 9))
        self.assertEquals([], p.parse_time("F-Z", 99))
        self.assertEquals([], p.parse_time("Z-Z", 99))

    def test_parse_keys_off(self):
        self.assertEquals(
            {
                'off': [
                    { "days": "M", "hour": 19 },
                    { "days": "T", "hour": 19 },
                    { "days": "W", "hour": 19 },
                    { "days": "H", "hour": 19 },
                    { "days": "F", "hour": 19 }
                ]
            },
            p.parse_keys("off=(M-F,19)")
        )
        self.assertEquals(
            {
                'off': [
                    { "days": "M", "hour": 21 },
                    { "days": "T", "hour": 21 },
                    { "days": "W", "hour": 21 },
                    { "days": "H", "hour": 21 },
                    { "days": "F", "hour": 21 },
                    { "days": "U", "hour": 18 }
                ]
            },
            p.parse_keys("off=[(M-F,21),(U,18)]")
        )
        #odd corner case
        #will get back to this one
        #self.assertEquals(None, p.parse_keys("off=[(M-F,21),(M,18)]"))
        self.assertEquals(None, p.parse_keys("off=[(M-F,21,123),(U,18)]"))
        self.assertEquals(None, p.parse_keys("off=[(M-Z,21),(U,18)]"))
        self.assertEquals(None, p.parse_keys("off=[(M-F,21),(U,99)]"))
        self.assertEquals(None, p.parse_keys("off=[(21,M-F),(U,99)]"))

    def test_parse_keys_on(self):
        self.assertEquals(
            {
                'on': [
                    { "days": "M", "hour": 19 },
                    { "days": "T", "hour": 19 },
                    { "days": "W", "hour": 19 },
                    { "days": "H", "hour": 19 },
                    { "days": "F", "hour": 19 }
                ]
            },
            p.parse_keys("on=(M-F,19)")
        )
        self.assertEquals(
            {
                'on': [
                    { "days": "M", "hour": 21 },
                    { "days": "T", "hour": 21 },
                    { "days": "W", "hour": 21 },
                    { "days": "H", "hour": 21 },
                    { "days": "F", "hour": 21 },
                    { "days": "U", "hour": 18 }
                ]
            },
            p.parse_keys("on=[(M-F,21),(U,18)]")
        )
        self.assertEquals(None, p.parse_keys("on=[(M-F,21,123),(U,18)]"))
        self.assertEquals(None, p.parse_keys("on=[(M-Z,21),(U,18)]"))
        self.assertEquals(None, p.parse_keys("on=[(M-F,21),(U,99)]"))
        self.assertEquals(None, p.parse_keys("on=[(21,M-F),(U,99)]"))

    def test_parse_keys_tz(self):
        self.assertEquals({'tz': 'et'}, p.parse_keys("tz=et"))
        self.assertEquals({'tz': 'pt'}, p.parse_keys("tz=pt"))
        self.assertEquals({'tz': 'et'}, p.parse_keys("tz="))
        self.assertEquals({'tz': 'et'}, p.parse_keys("tz=foo"))

    def test_parse_off_hours(self):
        self.assertEquals(
            {
                'off': [
                    { 'days': "M", 'hour': 19 },
                    { 'days': "T", 'hour': 19 },
                    { 'days': "W", 'hour': 19 },
                    { 'days': "H", 'hour': 19 },
                    { 'days': "F", 'hour': 19 }
                ],
                'on': [
                    { 'days': "M", 'hour': 7 },
                    { 'days': "T", 'hour': 7 },
                    { 'days': "W", 'hour': 7 },
                    { 'days': "H", 'hour': 7 },
                    { 'days': "F", 'hour': 7 }
                ],
                'tz': "pt"
            },
            p.parse_off_hours("off=(M-F,19);on=(M-F,7);tz=pt")
        )
        self.assertEquals(
            {
                'on': [
                    { 'days': "M", 'hour': 7 },
                    { 'days': "T", 'hour': 7 },
                    { 'days': "W", 'hour': 7 },
                    { 'days': "H", 'hour': 7 },
                    { 'days': "F", 'hour': 7 }
                ],
                'tz': "pt"
            },
            p.parse_off_hours("tz=pt;on=(M-F,7)")
        )
        self.assertEquals(
            {
                'off': [
                    { 'days': "M", 'hour': 19 },
                    { 'days': "T", 'hour': 19 },
                    { 'days': "W", 'hour': 19 },
                    { 'days': "H", 'hour': 19 },
                    { 'days': "F", 'hour': 19 }
                ],
                'on': [
                    { 'days': "M", 'hour': 7 },
                    { 'days': "T", 'hour': 7 },
                    { 'days': "W", 'hour': 7 },
                    { 'days': "H", 'hour': 7 },
                    { 'days': "F", 'hour': 7 }
                ],
                'tz': "et"
            },
            p.parse_off_hours("off=(M-F,19);on=(M-F,7)")
        )
        self.assertEquals(
            {
                'off': [
                    { 'days': "M", 'hour': 19 },
                    { 'days': "T", 'hour': 19 },
                    { 'days': "W", 'hour': 19 },
                    { 'days': "H", 'hour': 19 },
                    { 'days': "F", 'hour': 19 },
                    { 'days': "S", 'hour': 19 }
                ],
                'on': [
                    { 'days': "M", 'hour': 7 },
                    { 'days': "T", 'hour': 7 },
                    { 'days': "W", 'hour': 7 },
                    { 'days': "H", 'hour': 7 },
                    { 'days': "F", 'hour': 7 }
                ],
                'tz': "et"
            },
            p.parse_off_hours("off=[(M-F,19),(S,19)];on=(M-F,7)")
        )
        self.assertEquals(
            {
                'off': [
                    { 'days': "M", 'hour': 19 },
                    { 'days': "T", 'hour': 19 },
                    { 'days': "W", 'hour': 19 },
                    { 'days': "H", 'hour': 19 },
                    { 'days': "F", 'hour': 19 },
                    { 'days': "S", 'hour': 19 }
                ],
                'on': [
                    { 'days': "M", 'hour': 7 },
                    { 'days': "T", 'hour': 7 },
                    { 'days': "W", 'hour': 7 },
                    { 'days': "H", 'hour': 7 },
                    { 'days': "F", 'hour': 7 }
                ],
                'tz': "et"
            },
            p.parse_off_hours("off=[(M-F,19),(S,19)];on=(M-F,7);tz=foo")
        )
        self.assertEquals(
            None,
            p.parse_off_hours("off=[(Foo,19),(S,19)];on=(M-F,7)")
        )
        self.assertEquals(
            None,
            p.parse_off_hours("foo=[(M-F,19),(S,19)];on=(M-F,7)")
        )


if __name__ == '__main__':
    unittest.main()
