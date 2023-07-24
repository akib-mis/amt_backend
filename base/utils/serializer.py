import enum
from datetime import date, datetime
from json import JSONEncoder


class DefaultEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return str(obj).split(".")[0]
            elif isinstance(obj, date):
                return str(obj)
            if isinstance(obj, enum):
                return str(obj).split(".")[-1]
            else:
                return JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)
