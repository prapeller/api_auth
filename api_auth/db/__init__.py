from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


def init_models():
    from db.models import user  # noqa
    from db.models import role  # noqa
    from db.models import session  # noqa
    from db.models import social_account  # noqa
    from db.models import permission  # noqa
    from db.models import _association  # noqa


DATABASE_URL = f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@' \
               f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocalAsync = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
