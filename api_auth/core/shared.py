import datetime as dt
import json
import pathlib

from sqlalchemy.ext.hybrid import hybrid_property

SRC_PATH = pathlib.Path(__file__).resolve().parent.parent


class CustomEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        self.visited = set()
        super().__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, dt.datetime):
            return obj.isoformat()

        if hasattr(obj.__class__, '__table__'):
            return self.encode_sqlalchemy_model(obj)

        if isinstance(obj, hybrid_property):
            return getattr(obj.__self__, obj.__name__)

        return super().default(obj)

    def encode(self, obj):
        # Check for circular reference
        if id(obj) in self.visited:
            return None
        self.visited.add(id(obj))

        return super().encode(obj)

    def encode_sqlalchemy_model(self, obj):
        columns = obj.__table__.columns
        hybrid_properties = obj.__class__.__dict__.values()

        data = {}
        for column in columns:
            value = getattr(obj, column.name)
            if isinstance(value, dt.datetime):
                value = value.isoformat()
            data[column.name] = value

        for prop in hybrid_properties:
            if isinstance(prop, hybrid_property):
                data[prop.__name__] = getattr(obj, prop.__name__)

        return data
