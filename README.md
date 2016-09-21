# Cron Parser

A script to parse some cron tasks from stdin and determine their next run times from a specified time.

## Requirements
- Linux
- Python 2.7.10
- pip 8.1.2

## Project contents
```
bin/
  cron-parser
cron_parser/
  __init__.py
  cron_parser.py
cron_test.txt
README.md
requirements.txt
setup.py
test/
  test_cron_parser.py
```

## Installation instructions
```python
pip install -e .
pip install -r requirements.txt
```

## Testing
```python
py.test
```

## Usage
```
cron-parser -h
```
```
usage: cron-parser [-h] -t TIME

Parse cron tasks from stdin in format MM HH task

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  test time (HH:MM)
```

## Example
```
cat cron_test.txt
```
```
30 1 /bin/run_me_daily
45 * /bin/run_me_hourly
* * /bin/run_me_every_minute
* 19 /bin/run_me_sixty_times
```
```
cat cron_test.txt | cron-parser -t 12:00
```
```
01:30 tomorrow - /bin/run_me_daily
12:45 today - /bin/run_me_hourly
12:00 today - /bin/run_me_every_minute
19:00 today - /bin/run_me_sixty_times
```
