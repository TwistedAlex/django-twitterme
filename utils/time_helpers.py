from datetime import datetime
import pytz


def utc_now():
    return datetime.now().replace(tzinfo=pytz.utc)
