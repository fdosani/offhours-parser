from itertools import cycle
import re


valid_days = ('M', 'T', 'W', 'H', 'F', 'S', 'U')
valid_hours = tuple(h for h in xrange(1, 25))
valid_keys = ("off", "on", "tz")

tz_aliases = {
    'pdt': 'America/Los_Angeles',
    'pt': 'America/Los_Angeles',
    'pst': 'America/Los_Angeles',
    'est': 'America/New_York',
    'edt': 'America/New_York',
    'et': 'America/New_York',
    'cst': 'America/Chicago',
    'cdt': 'America/Chicago',
    'ct': 'America/Chicago',
    'mt': 'America/Denver',
    'gmt': 'Europe/London',
    'gt': 'Europe/London'
}

default_tz = 'et'

DEFAULT_TIMEZONE = 'et'
VALID_DAYS = ['M', 'T', 'W', 'H', 'F', 'S', 'U']


class ScheduleParser:

    cache = {}

    def parse(self, tag_value):
        # check the cache
        if tag_value in self.cache:
            return self.cache[tag_value]
        schedule = {}
        # parse schedule components
        pieces = tag_value.split(';')
        for piece in pieces:
            kv = piece.split('=')
            # components must by key-value
            if not len(kv) == 2:
                continue
            key = kv[0]
            value = kv[1]
            if key == 'on' or key == 'off':
                # parse custom on/off hours
                value = self.parse_custom_hours(value)
            schedule[key] = value
        # add default timezone, if none supplied
        if 'tz' not in schedule:
            schedule['tz'] = DEFAULT_TIMEZONE
        # validate
        if not self.is_valid(schedule):
            schedule = None
        # cache
        self.cache[tag_value] = schedule
        return schedule

    def parse_custom_hours(self, hours):
        parsed = []
        hours = hours.translate(None, '[]').split(',(')
        for hour in hours:
            hour = hour.translate(None, '()').split(',')
            # custom hours must have two parts: (<days>, <hour>)
            if not len(hour) == 2:
                continue
            try:
                hour[1] = int(hour[1])
            except ValueError:
                continue
            parsed.append({
                'days': self.expand_day_range(hour[0]),
                'hour': hour[1]
            })
        return parsed

    def expand_day_range(self, days):
        if len(days) == 1:
            return [days]
        days = days.split('-')
        if not len(days) == 2:
            return []
        # return a slice of valid days
        return VALID_DAYS[VALID_DAYS.index(days[0]):VALID_DAYS.index(days[1])+1]

    def is_valid(self, schedule):
        # off and on are both required if either is present
        if 'off' in schedule and 'on' not in schedule:
            return False
        elif 'on' in schedule and 'off' not in schedule:
            return False
        # validate custom on/off hours
        if 'off' in schedule and 'on' in schedule:
            if not self.is_valid_hours(schedule['off']):
                return False
            if not self.is_valid_hours(schedule['on']):
                return False
        return True

    def is_valid_hours(self, hours):
        if len(hours) <= 0:
            return False
        for hour in hours:
            if not self.is_valid_hour(hour):
                return False
        return True

    def is_valid_hour(self, hour):
        if len(hour['days']) <= 0:
            return False
        return True


def valid_day_range(days):
    """
    returns True or False based on if the input is a valid range
        format X-X where X is a valid day, and can't be the same like M-M
        or X where X is a valid day

    args:
        days (str):
            string denoting a date or a range of dates
    returns:
        boolean: True or False if the range is valid
    """
    if len(days) == 3:
        if days[0] == days[2]: return False
        elif days[0] in valid_days and days[1] == '-' and \
            days[2] in valid_days:
            return True
        else: return False
    elif len(days) == 1:
        return days in valid_days
    else:
        return False


def parse_time(days, hour):
    """
    function which takes in the days in the format:
        M-F , 21(range)
        or U, 10 (single)
    and returns the following dicts:
        {days : "M-F", hours: 21}
        {days : "U", hours: 10}

    args:
        days (str):
            string denoting a date or a range of dates
        hour (int):
            integer denoting a valid hour from 1 - 24
    returns:
        list: list of dictionaries with the k,v pair corresponding to the day and
        hour.
    """
    out = []
    #return None for invalid date range
    valid_day = valid_day_range(days)
    if not valid_day: return out

    #valid hours
    if not hour in valid_hours:
        return out

    #if a day range
    if not days in valid_days and len(days) == 3:
        inrange = False
        for d in cycle(valid_days):
            if days[0] == d:
                inrange = True
            if inrange:
                out.append({ "days": d, "hour": hour })
            if days[2] == d and inrange:
                inrange = False
                break
    #single day
    else:
        out.append({ "days": days, "hour": hour })
    return out


def parse_keys(item):
    """
    function which takes in a key, value format like:
        "off=(M-F,21),(U,18)"
    If will check to make sure the key is valid and also the value is properly
    formed. the proper formed item should consist of a key=(DAY,HOUR)[,(DAY,HOUR)]

    args:
        item (str):
            string comtaining the key value to parse
    returns:
        dict or None:

        list of dictionaries with days expanded if it was a range and the corresponding
        hour, for off and on
           {'off': [{ "days": "M", "hour": 21 },
                    { "days": "T", "hour": 21 },
                    { "days": "W", "hour": 21 },
                    { "days": "H", "hour": 21 },
                    { "days": "F", "hour": 21 },
                    { "days": "U", "hour": 18 }
                    ]}

            or {'tz': 'et'} if it is a timezone key

            if it is malformed or there is a error then it will return None
    """
    out = {}
    tl = []
    pair = item.split("=")
    if len(pair) != 2: return None #must be only 1 '='
    key, values = pair[0], pair[1]
    #remove [] from the string
    values = values.translate(None, "[]")
    if key in ('tz'):
        #defaut tz
        out[key] = default_tz
        if values in tz_aliases:
            out[key] = values
        return out
    #if someone passes a bad key then return None
    elif key in ('off', 'on'):
        #extract tuples. as long as the string is in the format
        # (aaa) (aaa) (aaa) it should be fine
        pattern = re.compile(r'\(([^)]*)\)')
        values = pattern.findall(values)
        out[key] = None #setup blank key
        for time in values: #iterate through list of dates
            time = time.split(",")
            if len(time) != 2: return None #we should be receiving 2 items
            #call parse_time. if it fails we will return None for malformed.
            try:
                pt = parse_time(time[0], int(time[1]))
            except:
                return None
            #If we get an empty list then we should return None
            if not len(pt): return None
            #append the lists if we have more than one
            tl = tl + pt
        #set the key to the final list of times
        out[key] = tl
        return out
    else:
        return None


def parse_off_hours(offhours):
    """
    main function whcich would be the starting point. it will parse out the
    input, for example: "off=(M-F,19);on=(M-F,7)"
    and return a dictionary such as:
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
                }
    args:
        offhours (str):
            string denoting a desired offhours schedule
    returns:
        dict or None
    """
    #create our base items
    output = {}
    items = offhours.split(';')
    for item in items:
        p = parse_keys(item)
        if not p:
            return None
        else:
            output.update(p)
    #if no tz then set the default one
    if not output.get('tz'):
        output['tz'] = default_tz
    return output
