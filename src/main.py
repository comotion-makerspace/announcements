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

TRIGGER_AT_MINUTES = [
                      30,
                      45,
                      55,
                     ]

TIME_FORMAT = "%m-%e-%y %H:%M"
FILLER = "fill..."
FILE_PREFIX="announcements"
BEGIN_FILE_PREFIX="begin"
AUDIO_PLAYER="mpg123"

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

def get_opening_hours():
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
    for minutes in TRIGGER_AT_MINUTES:
        minutes_to_close = 60 - minutes
        f="{}-{}.mp3".format(FILE_PREFIX, str(minutes_to_close))
        if not os.path.isfile(f):
            tts = gTTS('{} Attention! CoMotion Makerspace will close in {} minutes.'.format(FILLER, minutes_to_close),
                    lang='en')
            tts.save(f)
    f= "{}-{}.mp3".format(FILE_PREFIX, "0")
    if not os.path.isfile(f):
        tts = gTTS('{} Attention! ... the makerspace is now closed.'
                    'Unless authorized, please pack your belongings and exit.'
                    'Thank you, have a wonderful evening!'.format(FILLER))
        tts.save(f)
    f= "{}-{}.mp3".format(FILE_PREFIX, BEGIN_FILE_PREFIX)
    if not os.path.isfile(f):
        tts= gTTS('{} closing announcements are now running'.format(FILLER))
        tts.save(f)

def announce_closing(minutes):
    if minutes == 0:
        minutes_to_close = 0
        logging.info('Announced MakerSpace closed @ {}'.format(datetime.datetime.strftime(TIME_FORMAT)))
    else:
        minutes_to_close = 60 - minutes
        logging.info('Announced pre-closing time: {} minutes before'.format(minutes_to_close))
    os.system('{} {}-{}.mp3'.format(AUDIO_PLAYER, FILE_PREFIX, str(minutes_to_close)))

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
        today = datetime.datetime.isoweekday(current)
        for d in data:
            if d['dayOfWeek'] == today:
                closing = datetime.datetime.strptime(d['untilTime'], '%H:%M')
                if closing.hour - current.hour == 0 or \
                (closing.hour + 1 - current.hour == 0 and current.minute == 0):
                    if current.minute in TRIGGER_AT_MINUTES or current.minute == 0:
                        announce_closing(current.minute)

schedule.every().day.at('03:00').do(get_opening_hours)
schedule.every().minute.at(':00').do(check_announcement_time)

def run_once():
    logging.info('Program started. Time is {}'.format(time.strftime(TIME_FORMAT)))
    get_opening_hours()
    get_speech_snippets()
    os.system('{} {}-{}.mp3'.format(AUDIO_PLAYER, FILE_PREFIX, BEGIN_FILE_PREFIX)) # TODO:
run_once()

while True:
    schedule.run_pending()
    time.sleep(1)