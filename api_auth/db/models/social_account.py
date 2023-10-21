import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated


class SocialAccountModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'social_account'

    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'))
    user = relationship('UserModel', back_populates='social_accounts', lazy='selectin')

    social_name = sa.Column(sa.String(20))
    social_uuid = sa.Column(sa.String(50))

    __table_args__ = (
        sa.UniqueConstraint(
            'user_uuid', 'social_uuid', name='unique_user_uuid_social_uuid'),
    )

    def __repr__(self):
        return f'<SocialAccountModel> ({self.id=:}, {self.created_at=:}, {self.user_uuid=:}, ' \
               f'{self.social_name=:}, {self.social_uuid=:})'
