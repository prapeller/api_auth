import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship

from db import Base
from db.models._association import UserRoleAssociation, RolePermissionAssociation
from db.models._shared import IdentifiedCreatedUpdated
from db.models.permission import PermissionModel


class RoleModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'role'

    name = sa.Column(sa.String(20), unique=True, nullable=False)
    users = relationship('UserModel', secondary='user_role', back_populates='roles', lazy='selectin')
    permissions = relationship('PermissionModel', secondary='role_permission', back_populates='roles', lazy='selectin')

    @hybrid_property
    def users_uuids(self):
        return [user.uuid for user in self.users]

    @users_uuids.expression
    def users_uuids(cls):
        return sa.select(UserRoleAssociation.user_uuid).filter_by(role_uuid=cls.uuid)

    @hybrid_property
    def permissions_uuids(self):
        return [perm.uuid for perm in self.permissions]

    @permissions_uuids.setter
    def permissions_uuids(self, permissions_ids):
        session = object_session(self)
        self.permissions = session.query(PermissionModel).filter(PermissionModel.uuid.in_(permissions_ids)).all()

    @permissions_uuids.expression
    def permissions_uuids(cls):
        return sa.select(RolePermissionAssociation.permission_uuid).filter_by(role_uuid=cls.uuid)

    @hybrid_property
    def permissions_names(self):
        return [perm.name for perm in self.permissions]

    @permissions_names.expression
    def permissions_names(cls):
        return (
            sa.select(PermissionModel.name)
            .join(RolePermissionAssociation)
            .where(RolePermissionAssociation.permission_uuid == cls.uuid)
        )

    def __repr__(self):
        return f'<RoleModel> ({self.uuid=:}, {self.name=:})'
