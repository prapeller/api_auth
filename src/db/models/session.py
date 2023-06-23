import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated


class SessionModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'session'

    user_id = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('UserModel', back_populates='sessions')

    useragent = sa.Column(sa.String(512))
    ip = sa.Column(sa.String(39))
    is_active = sa.Column(sa.Boolean, default=True)

    def __repr__(self):
        return f'<SessionModel> ({self.id=:}, {self.created_at=:}, {self.user=:}, ' \
               f'{self.useragent=:}, {self.ip=:}, {self.is_active=:})'
