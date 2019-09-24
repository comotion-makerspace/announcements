import os

FILE_PREFIX="announcements"
BEGIN_FILE_PREFIX="begin"
AUDIO_PLAYER="mpg123"
NOTIFICATION_SOUND="doorbell.mp3"

for i in range(0, 3):
    os.system('{} {}'.format(AUDIO_PLAYER, NOTIFICATION_SOUND))
    os.system('{} {}-{}.mp3'.format(AUDIO_PLAYER, FILE_PREFIX, BEGIN_FILE_PREFIX))