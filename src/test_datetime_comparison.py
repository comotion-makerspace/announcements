import datetime
import pytest

TRIGGER_AT_MINUTES_IN_CLOSING_HOUR = [
                      15,
                      30,
                      45,
                      55,
                      59,
                     ]

def test_compare_datetimes_trigger_announcement(current_time, closing_time):
    assert closing_time.isoweekday() == current_time.isoweekday(), "Not the same day"
    if closing_time.isoweekday() == current_time.isoweekday():
        # # Check if the makerspace is closing in the next hour:
        closing_hour = False
        assert closing_time.hour - (current_time.hour + 1) == 0, "Not a closing hour"
        if closing_time.hour - (current_time.hour + 1) == 0:
            closing_hour = True
        assert closing_hour and current_time.minute != 0, "Closing hour minute is not 0"
        if closing_hour and current_time.minute != 0:
            assert current_time.minute in TRIGGER_AT_MINUTES_IN_CLOSING_HOUR, "Minute not in TRIGGER_AT_MINUTES_IN_CLOSING_HOUR"
            # if current_time.minute in TRIGGER_AT_MINUTES_IN_CLOSING_HOUR:
            #     announce(current_time.minute)

        # Check if the makerspace is now closed
        assert closing_time.hour - current_time.hour == 0, "Not closed"
        is_closed = closing_time.hour - current_time.hour == 0
        assert is_closed and current_time.minute == 0, "Closed in same hour but not the exact minute of closure (0)"
        # if is_closed and current_time.minute == 0:
        #     announce(closed=True)

@pytest.fixture
def closing_time():
    ''' simulate a closing hour of 8pm'''
    closing_time = datetime.datetime.now() 
    closing_time = closing_time.replace(hour=20, minute=0)
    return closing_time
# def closing_time():
#     ''' test different days; since the isoweekday is %7 we need to choose the day of the month using the replace method:
#     '''
#     closing_time = datetime.datetime.now() 
#     closing_time = closing_time.replace(day=23)
#     return closing_time


@pytest.fixture
def current_time():
    '''test the current hour is the closing hour or that the makerspace is now closed (closing hour at minute 0)'''
    current_time = datetime.datetime.now()
    # will fail unless assertion for "Not a closing hour" is commented out
    # current_time = current_time.replace(hour=20, minute=0)  # 8pm and exact minute of closing (0)
    # current_time = current_time.replace(hour=19, minute=0)  # 7pm but fails since minute is 0
    # will fail unless assertion for "Not closed" is commented out
    # also comment out "Closed in same hour but not the exact time of closure where minute=0"
    current_time = current_time.replace(hour=20, minute=1)  # 7pm but fails since minute is 0
    return current_time
# def current_time():
#     '''test different hours and minutes within the closing hour; edge case is the closing hour and 0 minute'''
#     current_time = datetime.datetime.now()
#     current_time = current_time.replace(hour=19, minute=1)  # 7pm passes since minute is not 0
#     # current_time = current_time.replace(hour=19, minute=0)  # 7pm but fails since minute is 0
#     return current_time
# def current_time():
#     '''test different hours by checking if the current hour is within the closing hour'''
#     current_time = datetime.datetime.now()
#     # current_time = current_time.replace(hour=18, minute=30) # 6pm
#     current_time = current_time.replace(hour=2, minute=45)  # 2am
#     # current_time = current_time.replace(hour=19, minute=0)  # 7pm
#     return current_time
# def current_time():
#     ''' test different days by checking if the current day is the same as a closing day'''
#     current_time = datetime.datetime.now() 
#     return current_time