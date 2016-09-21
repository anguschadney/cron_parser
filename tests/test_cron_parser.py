from datetime import date, datetime
import subprocess

from mock import patch
import pytest

from cron_parser.cron_parser import CronTask


def test_wild():
    assert CronTask.is_wild('*')
    assert not CronTask.is_wild('10')
    assert CronTask.both_wild('*', '*')
    assert not CronTask.both_wild('15', '*')
    assert not CronTask.both_wild('*', '20')


def test_get_test_time():
    today = datetime(2016, 1, 1)
    test_time = datetime(2016, 1, 1, 12, 30)
    assert CronTask.get_test_time(today, '12:30') == test_time


@pytest.mark.parametrize('next_run, day', [
    (datetime(2016, 1, 1, 0, 0), 'today'),
    (datetime(2016, 1, 1, 12, 0), 'today'),
    (datetime(2016, 1, 2, 0, 0), 'tomorrow'),
])
def test_get_next_run_day(next_run, day):
    today = datetime(2016, 1, 1)
    assert CronTask.get_next_run_day(today, next_run) == day


@pytest.mark.parametrize('minute, hour, time, result', [
    # Neither minute or hour is wild
    ('30', '12', '00:00', '2016-01-01 12:30:00'),
    ('30', '12', '12:30', '2016-01-01 12:30:00'),
    ('30', '12', '23:59', '2016-01-02 12:30:00'),
    # Minute is wild
    ('*', '12', '00:00', '2016-01-01 12:00:00'),
    ('*', '12', '12:00', '2016-01-01 12:00:00'),
    ('*', '12', '12:30', '2016-01-01 12:30:00'),
    ('*', '12', '13:00', '2016-01-02 12:00:00'),
    # Hour is wild
    ('30', '*', '00:00', '2016-01-01 00:30:00'),
    ('30', '*', '12:00', '2016-01-01 12:30:00'),
    ('30', '*', '12:30', '2016-01-01 12:30:00'),
    ('30', '*', '12:45', '2016-01-01 13:30:00'),
    ('30', '*', '23:45', '2016-01-02 00:30:00'),
    # Both hour and minute is wild
    ('*', '*', '00:00', '2016-01-01 00:00:00'),
    ('*', '*', '12:01', '2016-01-01 12:01:00'),
    ('*', '*', '23:59', '2016-01-01 23:59:00'),
])
@patch('cron_parser.cron_parser.date')
def test_cron_task_runs(mock_date, minute, hour, time, result):
    mock_date.today.return_value = datetime(2016, 1, 1)
    mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

    cron_task = CronTask(minute, hour, 'test')
    cron_task.get_next_run(time)
    assert str(cron_task.next_run) == result


def test_display_next_run():
    cron_task = CronTask('00', '12', 'test')
    cron_task.get_next_run('00:00')

    assert cron_task.display_next_run() == '12:00 today - test\n'


def test_run_script():
    cron_input = subprocess.Popen(
        ['echo', '30 11 test'],
        stdout=subprocess.PIPE,
    )
    script = subprocess.Popen(
        ['cron-parser', '-t', '00:00'],
        stdin=cron_input.stdout,
        stdout=subprocess.PIPE,
    )
    out = script.stdout.readline()
    assert out == '11:30 today - test\n'
