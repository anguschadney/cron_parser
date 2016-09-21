from datetime import date, datetime, time, timedelta

from pandas import date_range


MIDNIGHT = time()
WILD_CHAR = '*'


class CronTask(object):
    """Object to store a single cron task and calculate run times.

    Args:
        minute (str): minute past the hour (00-59) (* is wild / all valid vals)
        hour (str): hour of the day (00-23) (* is wild / all valid vals)
        command (str): command to run

    Attributes:
        command (str): command to run
        _today_midnight (datetime): today's datetime at midnight
        run_range (pandas DatetimeIndex): range of valid run times for current
                                          day plus the earliest valid run time
                                          tomorrow.
        next_run (datetime): datetime of next valid run time for a particular
                             test time.
    """

    def __init__(self, minute, hour, command):
        self.command = command
        self._today_midnight = datetime.combine(date.today(), MIDNIGHT)
        self.run_range = self.get_run_range(minute, hour)
        self.next_run = None

    @staticmethod
    def is_wild(time_unit):
        return time_unit == WILD_CHAR

    @classmethod
    def both_wild(cls, minute, hour):
        return cls.is_wild(minute) and cls.is_wild(hour)

    @staticmethod
    def get_test_time(today_midnight, time_string):
        hour, minute = time_string.split(':')
        return today_midnight.replace(hour=int(hour), minute=int(minute))

    @staticmethod
    def get_next_run_day(today_midnight, next_run):
        if next_run >= today_midnight + timedelta(days=1):
            return 'tomorrow'
        return 'today'

    def get_run_range(self, minute, hour):
        """Calculate range of run times for cron task.

        Args:
            minute (str): minute past the hour (00-59) (* is wild)
            hour (str): hour of the day (00-23) (* is wild)

        Returns:
            pandas DatetimeIndex containing valid run datetimes for today
            plus the first valid run time tomorrow.
        """
        today_midnight = self._today_midnight

        # Minutes and hours are wild ('*')
        # Create range from 00:00 to 00:00 (day+1) in intervals of 1 min
        if self.both_wild(minute, hour):
            start = today_midnight
            end = today_midnight + timedelta(days=1)
            return date_range(start, end, freq='1 min')

        # Only hours are wild ('*')
        # Create range from 00:XX to 00:XX (day+1) in intervals of 1 hour
        # XX = defined minutes
        if self.is_wild(hour):
            start = today_midnight + timedelta(minutes=int(minute))
            end = today_midnight + timedelta(days=1, hours=1)
            return date_range(start, end, freq='60 min')

        # Only minutes are wild ('*')
        # Create range from XX:00 to XX:59 in intervals of 1 minutes
        # Also tack on the first valid datetime tomorrow (day+1) in case we
        # have already passed this range
        # XX = defined hours
        if self.is_wild(minute):
            start = today_midnight + timedelta(hours=int(hour))
            end = start + timedelta(minutes=59)
            run_range = date_range(start, end, freq='1 min')
            tomorrow_start = [start + timedelta(days=1)]
            return run_range.union(tomorrow_start)

        # Both hour and minute is defined
        # Create range from XX:YY to XX:YY (day+1) in intervals of 1 day
        # XX = defined hours, YY = defined minutes
        start = today_midnight + timedelta(
            hours=int(hour), minutes=int(minute)
        )
        end = start + timedelta(days=1)
        return date_range(start, end, freq='1D')

    def get_next_run(self, time_string):
        """Calculate range of run times for cron task.

        Args:
            time_string (str): test time from which next run will be
                               calculated (HH:MM)

        Sets self.next_run to the datetime of the next run time
        """
        today_midnight = self._today_midnight
        test_time = self.get_test_time(today_midnight, time_string)
        # asof(time) will return the element of the DatetimeIndex closest to
        # time (rounding down).  Therefore the range is reversed using [::-1]
        # so that we return the next valid time cronologically.
        self.next_run = self.run_range[::-1].asof(test_time)

    def display_next_run(self):
        command = self.command
        time_string = self.next_run.strftime('%H:%M')
        day = self.get_next_run_day(self._today_midnight, self.next_run)
        return('{} {} - {}\n'.format(time_string, day, command))
