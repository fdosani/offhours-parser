DEFAULT_TZ = 'et'
VALID_DAYS = ['M', 'T', 'W', 'H', 'F', 'S', 'U']
VALID_HOURS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
               19, 20, 21, 22, 23)


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
            schedule['tz'] = DEFAULT_TZ
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
                #force an all or nothing senario in terms of bad values
                return []
            try:
                hour[1] = int(hour[1])
                if not self.is_valid_hour_range(hour[1]):
                    raise ValueError
                parsed.append({
                    'days': self.expand_day_range(hour[0]),
                    'hour': hour[1]
                    })
            except ValueError:
                #force an all or nothing senario in terms of bad values
                return []
        return parsed

    def expand_day_range(self, days):
        if len(days) == 1:
            if not self.is_valid_day(days):
                raise ValueError
            return [days]

        days = days.split('-')
        if not len(days) == 2:
            return []

        if not self.is_valid_day(days[0]) or not self.is_valid_day(days[1]):
            raise ValueError
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

    def is_valid_hour_range(self, hour):
        if hour in VALID_HOURS:
            return True
        return False

    def is_valid_day(self, day):
        if day in VALID_DAYS:
            return True
        return False
