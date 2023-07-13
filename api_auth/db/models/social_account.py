import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated


class SocialAccountModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'social_account'

    user_id = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('UserModel', back_populates='social_accounts', lazy='selectin')

    social_name = sa.Column(sa.String(20))
    social_id = sa.Column(sa.String(50))

    __table_args__ = (
        sa.UniqueConstraint(
            'user_id', 'social_id', name='unique_user_id_social_id'),
    )

    def __repr__(self):
        return f'<SocialAccountModel> ({self.id=:}, {self.created_at=:}, {self.user_id=:}, ' \
               f'{self.social_name=:}, {self.social_id=:})'
