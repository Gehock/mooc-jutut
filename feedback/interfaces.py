import logging
from functools import wraps, partial
from datetime import datetime, timezone

from aplus_client.client import AplusGraderClient


DATETIME_JSON_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'

logger = logging.getLogger(__name__)


def none_on_error(*args, exceptions=None):
    if not args:
        return partial(none_on_error, exceptions=exceptions)
    if len(args) > 1 or (isinstance(args[0], type) and issubclass(args[0], Exception)):
        return partial(none_on_error, exceptions=args)

    func = args[0]
    exceptions = tuple(set([AttributeError] + (list(exceptions) if exceptions else [])))

    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            logger.info("interface %s raised exception %s", func.__name__, e)
            return None
    return wrap


class AplusJututClient(AplusGraderClient):
    @property
    def grading_data(self):
        return GraderInterface2(super().grading_data)


class GraderInterface2:
    def __init__(self, data):
        if not hasattr(data, '_client'):
            raise RuntimeError
        self.data = data

    @property
    @none_on_error
    def exercise(self):
        return self.data.exercise

    @property
    @none_on_error
    def course(self):
        return self.data.exercise.course

    @property
    @none_on_error
    def language(self):
        return self.data.exercise.course.language or None

    @property
    @none_on_error(KeyError)
    def form_spec(self):
        return self.data.exercise.exercise_info.get_item('form_spec')

#uusi
    @property
    @none_on_error(KeyError)
    def form_i18n(self):
        return self.data.exercise.exercise_info.get_item('form_i18n')

    @property
    @none_on_error
    def submission_id(self):
        return self.data.submission.id

    @property
    @none_on_error
    def submitters(self):
        return self.data.submission.submitters

    @property
    @none_on_error(ValueError)
    def submission_time(self):
        time = self.data.submission.submission_time
        return datetime.strptime(time, DATETIME_JSON_FMT).replace(tzinfo=timezone.utc) if time else None

    @property
    @none_on_error(KeyError)
    def html_url(self):
        return self.data.submission.get_item('html_url')