import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated


class PermissionModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'permission'

    name = sa.Column(sa.String(20), unique=True, nullable=False)

    # many-to-many
    roles = relationship('RoleModel', secondary='role_permission', back_populates='permissions', lazy='selectin')

    def __repr__(self):
        return f"<PermissionModel> ({self.id=:}, {self.name=:})"
