import requests
import schedule
import colorlog
import time
import os
import pickle
import json
import datetime
import logging
from gtts import gTTS

TRIGGER_AT_MINUTES_IN_CLOSING_HOUR = [
                      15,
                      30,
                      45,
                      55,
                      59,
                     ]

TIME_FORMAT = "%m-%e-%y %H:%M"
FILLER = "" # now unnecessary
FILE_PREFIX="announcements"
BEGIN_FILE_PREFIX="begin"
AUDIO_PLAYER="mpg123"
NOTIFICATION_SOUND="doorbell.mp3"

LOG_LEVEL = logging.INFO
LOG_FILENAME = 'closing_announcements.log'

API_KEY = os.environ['FABMAN_API_KEY']
SPACE = os.environ['FABMAN_SPACE']

# Logger
log = logging.getLogger()
log.setLevel(LOG_LEVEL) 

fmt = ("%(asctime)s %(levelname)s -> %(message)s")
datefmt = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME, format=fmt, datefmt=datefmt)
logging.getLogger('schedule').setLevel(logging.WARNING)

# Color logger (only on terminal for now)
# logging.config.fileConfig(colorlog)

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s'))
logger = colorlog.getLogger()
logger.addHandler(handler)

logging.info('program started')

def get_opening_hours(use_pickle=False):
    if use_pickle:
        print('got data from pickle')
        try:
            with open('data.pickle', 'rb') as f:
                data = pickle.load(f)
        except (OSError, IOError) as e:
            logging.error('could not find closing time data; attempting to fetch from web...'
                        '\n{}'.format(e))
    else:
        headers = {'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(API_KEY)}
        r = requests.get('https://fabman.io/api/v1/spaces/{}/opening-hours'
                        .format(SPACE), headers=headers)
        if r.status_code == 200 and r.json():
            with open('data.pickle', 'wb') as f:
                pickle.dump(r.json(), f, pickle.HIGHEST_PROTOCOL)
            logging.info('Fetching opening hours')
        else:
            logging.warning('Unable to fetch opening hours')

def get_speech_snippets():
    for minutes in TRIGGER_AT_MINUTES_IN_CLOSING_HOUR:
        minutes_to_close = 60 - minutes
        f="{}-{}.mp3".format(FILE_PREFIX, str(minutes_to_close))
        if not os.path.isfile(f):
            tts = gTTS('{} Attention! The Makerspace will close in {} minutes.'.format(FILLER, minutes_to_close),
                    lang='en')
            tts.save(f)
    f= "{}-{}.mp3".format(FILE_PREFIX, "0")
    if not os.path.isfile(f):
        tts = gTTS('{} Attention! The makerspace is now closed. '
                    'Unless authorized, please pack your belongings and exit. '
                    'Thank you, have a wonderful evening!'.format(FILLER))
        tts.save(f)
    f= "{}-{}.mp3".format(FILE_PREFIX, BEGIN_FILE_PREFIX)
    if not os.path.isfile(f):
        tts= gTTS('{} closing announcements are now running'.format(FILLER))
        tts.save(f)

def announce_closing(minutes):
    if minutes == 0:
        minutes_to_close = 0
        logging.info('Announced MakerSpace closed @ {}'.format(time.strftime(TIME_FORMAT)))
    else:
        minutes_to_close = 60 - minutes
        logging.info('Announced pre-closing time: {} minutes before'.format(minutes_to_close))
    os.system('{} {}'.format(AUDIO_PLAYER, NOTIFICATION_SOUND))
    os.system('{} {}-{}.mp3'.format(AUDIO_PLAYER, FILE_PREFIX, str(minutes_to_close)))

def compare_datetimes_trigger_announcement(current_time, day_of_week, closing_time):
    if day_of_week == current_time.isoweekday():
        # Check if the makerspace is closing in the next hour:
        closing_hour = False
        if closing_time.hour - (current_time.hour + 1) == 0:
            closing_hour = True
        if closing_hour and current_time.minute != 0:
            if current_time.minute in TRIGGER_AT_MINUTES_IN_CLOSING_HOUR:
                announce_closing(current_time.minute)

        # Check if the makerspace is now closed
        is_closed = closing_time.hour - current_time.hour == 0
        if is_closed and current_time.minute == 0:
            announce_closing(current_time.minute)

def check_announcement_time():
    data = None
    try:
        with open('data.pickle', 'rb') as f:
            data = pickle.load(f)
    except (OSError, IOError) as e:
        logging.error('could not find closing time data'
                      '\n{}'.format(e))
    if data:
        current = datetime.datetime.now()
        for d in data:
            closing = datetime.datetime.strptime(d['untilTime'], '%H:%M')
            compare_datetimes_trigger_announcement(current, d['dayOfWeek'], closing)

schedule.every().day.at('03:00').do(get_opening_hours)
schedule.every().minute.at(':00').do(check_announcement_time)

def run_once():
    logging.info('Program started. Time is {}'.format(time.strftime(TIME_FORMAT)))
    get_opening_hours()
    get_speech_snippets()
run_once()

while True:
    schedule.run_pending()
    time.sleep(1)