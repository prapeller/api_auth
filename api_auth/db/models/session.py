import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated


class SessionModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'session'

    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'))
    user = relationship('UserModel', back_populates='sessions', lazy='selectin')

    useragent = sa.Column(sa.String(512))
    ip = sa.Column(sa.String(39))
    is_active = sa.Column(sa.Boolean, default=True)

    def __repr__(self):
        return f'<SessionModel> ({self.id=:}, {self.created_at=:}, {self.useragent=:}, {self.ip=:}, {self.is_active=:})'
