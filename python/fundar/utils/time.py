from fundar.utils import staticproperty
from datetime import datetime, timedelta
from timeit import default_timer

class now:
    # noinspection PyMethodParameters
    @staticproperty
    def string():
        return datetime.now().strftime('%d-%m-%y_%H%M%S')

def stopwatch(f: callable, *args, **kwargs):
    start = default_timer()
    result = f(*args, **kwargs)
    elapsed_time = default_timer() - start
    return result, timedelta(seconds=elapsed_time)

def parse_time(time_string, timezone=None):
    original_datetime = datetime.fromisoformat(time_string.replace("Z", "+00:00"))
    if not timezone:
        return original_datetime
    
    timezone = pytz.timezone(timezone)
    return original_datetime.astimezone(timezone)

def parse_timex(timezone):
    return lambda time_string: parse_time(time_string, timezone=timezone)

parse_time_arg = parse_timex('America/Argentina/Buenos_Aires')

def format_time(time_object, format):
    return time_object.strftime(format)

def format_timex(format):
    return lambda time_object: format_time(time_object, format)

timeformat = format_timex("%d-%m-%y_%H%M%S")