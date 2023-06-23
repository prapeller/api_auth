import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings


def init_db():
    from db.models import user  # noqa
    from db.models import role  # noqa
    from db.models import session  # noqa
    from db.models import permission  # noqa
    from db.models import _association  # noqa


DATABASE_URL = f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@' \
               f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
engine = sa.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
