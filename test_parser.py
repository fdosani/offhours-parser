import unittest
import parser as p



class ParserTest(unittest.TestCase):

    def test_valid_day_range(self):
        #valid
        test = p.valid_day_range("M-F")
        self.assertTrue(test)

        #valid
        test = p.valid_day_range("W-S")
        self.assertTrue(test)

        #valid
        test = p.valid_day_range("F-T")
        self.assertTrue(test)

        #invalid
        test = p.valid_day_range("F-F")
        self.assertFalse(test)

        #invalid range but ok otherwise as a single Day
        test = p.valid_day_range("M")
        self.assertTrue(test)

        test = p.valid_day_range("U")
        self.assertTrue(test)

        #invalid
        test = p.valid_day_range("Z")
        self.assertFalse(test)



    def test_parse_time(self):
        test = p.parse_time("M", 9)
        expected = [{ "days": "M", "hour": 9 }]
        self.assertEquals(test, expected)

        test = p.parse_time("W", 19)
        expected = [{ "days": "W", "hour": 19 }]
        self.assertEquals(test, expected)

        test = p.parse_time("W", 99)
        expected = []
        self.assertEquals(test, expected)

        test = p.parse_time("Z", 9)
        expected = []
        self.assertEquals(test, expected)

        test = p.parse_time("Z", 99)
        expected = []
        self.assertEquals(test, expected)


        test = p.parse_time("M-F", 9)
        expected = [{ "days": "M", "hour": 9 },
                    { "days": "T", "hour": 9 },
                    { "days": "W", "hour": 9 },
                    { "days": "H", "hour": 9 },
                    { "days": "F", "hour": 9 }
                    ]
        self.assertEquals(test, expected)



        test = p.parse_time("F-T", 9)
        expected = [{ "days": "F", "hour": 9 },
                    { "days": "S", "hour": 9 },
                    { "days": "U", "hour": 9 },
                    { "days": "M", "hour": 9 },
                    { "days": "T", "hour": 9 }
                    ]
        self.assertEquals(test, expected)


        test = p.parse_time("F-T", 99)
        expected = []
        self.assertEquals(test, expected)


        test = p.parse_time("F-F", 9)
        expected = []
        self.assertEquals(test, expected)


        test = p.parse_time("F-Z", 99)
        expected = []
        self.assertEquals(test, expected)


        test = p.parse_time("Z-Z", 99)
        expected = []
        self.assertEquals(test, expected)



    def test_parse_keys_off(self):
        test = p.parse_keys("off=(M-F,19)")
        expected = {'off': [{ "days": "M", "hour": 19 },
                    { "days": "T", "hour": 19 },
                    { "days": "W", "hour": 19 },
                    { "days": "H", "hour": 19 },
                    { "days": "F", "hour": 19 }
                    ]}
        self.assertEquals(test, expected)

        test = p.parse_keys("off=[(M-F,21),(U,18)]")
        expected = {'off': [{ "days": "M", "hour": 21 },
                    { "days": "T", "hour": 21 },
                    { "days": "W", "hour": 21 },
                    { "days": "H", "hour": 21 },
                    { "days": "F", "hour": 21 },
                    { "days": "U", "hour": 18 }
                    ]}
        self.assertEquals(test, expected)



        #odd corner case
        #will get back to this one
        #test = p.parse_keys("off=[(M-F,21),(M,18)]")
        #expected = None
        #self.assertEquals(test, expected)


        test = p.parse_keys("off=[(M-F,21,123),(U,18)]")
        expected = None
        self.assertEquals(test, expected)


        test = p.parse_keys("off=[(M-Z,21),(U,18)]")
        expected = None
        self.assertEquals(test, expected)


        test = p.parse_keys("off=[(M-F,21),(U,99)]")
        expected = None
        self.assertEquals(test, expected)

        test = p.parse_keys("off=[(21,M-F),(U,99)]")
        expected = None
        self.assertEquals(test, expected)



    def test_parse_keys_on(self):
        test = p.parse_keys("on=(M-F,19)")
        expected = {'on': [{ "days": "M", "hour": 19 },
                    { "days": "T", "hour": 19 },
                    { "days": "W", "hour": 19 },
                    { "days": "H", "hour": 19 },
                    { "days": "F", "hour": 19 }
                    ]}
        self.assertEquals(test, expected)

        test = p.parse_keys("on=[(M-F,21),(U,18)]")
        expected = {'on': [{ "days": "M", "hour": 21 },
                    { "days": "T", "hour": 21 },
                    { "days": "W", "hour": 21 },
                    { "days": "H", "hour": 21 },
                    { "days": "F", "hour": 21 },
                    { "days": "U", "hour": 18 }
                    ]}
        self.assertEquals(test, expected)


        test = p.parse_keys("on=[(M-F,21,123),(U,18)]")
        expected = None
        self.assertEquals(test, expected)


        test = p.parse_keys("on=[(M-Z,21),(U,18)]")
        expected = None
        self.assertEquals(test, expected)


        test = p.parse_keys("on=[(M-F,21),(U,99)]")
        expected = None
        self.assertEquals(test, expected)

        test = p.parse_keys("on=[(21,M-F),(U,99)]")
        expected = None
        self.assertEquals(test, expected)



    def test_parse_keys_tz(self):
        test = p.parse_keys("tz=et")
        expected = {'tz': 'et'}
        self.assertEquals(test, expected)

        test = p.parse_keys("tz=pt")
        expected = {'tz': 'pt'}
        self.assertEquals(test, expected)

        test = p.parse_keys("tz=")
        expected = {'tz': 'et'}
        self.assertEquals(test, expected)

        test = p.parse_keys("tz=foo")
        expected = {'tz': 'et'}
        self.assertEquals(test, expected)



    def test_parse_off_hours(self):
        test = p.parse_off_hours("off=(M-F,19);on=(M-F,7);tz=pt")
        expected = {
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
                    }
        self.assertEquals(test, expected)


        test = p.parse_off_hours("tz=pt;on=(M-F,7)")
        expected = {
                      'on': [
                        { 'days': "M", 'hour': 7 },
                        { 'days': "T", 'hour': 7 },
                        { 'days': "W", 'hour': 7 },
                        { 'days': "H", 'hour': 7 },
                        { 'days': "F", 'hour': 7 }
                      ],
                      'tz': "pt"
                    }
        self.assertEquals(test, expected)


        test = p.parse_off_hours("off=(M-F,19);on=(M-F,7)")
        expected = {
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
                    }
        self.assertEquals(test, expected)



        test = p.parse_off_hours("off=[(M-F,19),(S,19)];on=(M-F,7)")
        expected = {
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
                    }
        self.assertEquals(test, expected)



        test = p.parse_off_hours("off=[(M-F,19),(S,19)];on=(M-F,7);tz=foo")
        expected = {
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
                    }
        self.assertEquals(test, expected)



        test = p.parse_off_hours("off=[(Foo,19),(S,19)];on=(M-F,7)")
        expected = None
        self.assertEquals(test, expected)

        test = p.parse_off_hours("foo=[(M-F,19),(S,19)];on=(M-F,7)")
        expected = None
        self.assertEquals(test, expected)




if __name__ == '__main__':
    unittest.main()
