import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from db import Base
from db.models._association import UserRoleAssociation, RolePermissionAssociation
from db.models._shared import IdentifiedCreatedUpdated
from db.models.permission import PermissionModel
from db.models.role import RoleModel
from db.models.session import SessionModel


class UserModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'user'

    email = sa.Column(sa.String(50), unique=True, index=True)
    name = sa.Column(sa.String(50))
    password = sa.Column(sa.String(100))
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)

    # many-to-many
    roles = relationship('RoleModel', secondary='user_role', back_populates='users', lazy='selectin')
    # many-to-one
    sessions = relationship('SessionModel', back_populates='user', lazy='selectin')
    social_accounts = relationship('SocialAccountModel', back_populates='user', lazy='selectin')

    @hybrid_property
    def roles_uuids(self):
        return [role.uuid for role in self.roles]

    @roles_uuids.expression
    def roles_uuids(cls):
        return sa.select(UserRoleAssociation.role_uuid).filter_by(user_uuid=cls.uuid)

    @hybrid_property
    def permissions_uuids(self):
        return [perm.uuid for perm in self.permissions]

    @permissions_uuids.expression
    def permissions_uuids(cls):
        return (sa.select(PermissionModel.uuid)
                .join(RolePermissionAssociation)
                .join(RoleModel)
                .join(cls.roles)
                .where(UserRoleAssociation.user_uuid == cls.uuid)
                )

    @hybrid_property
    def sessions_uuids(self):
        return [session.uuid for session in self.sessions]

    @sessions_uuids.expression
    def sessions_uuids(cls):
        return sa.select(SessionModel.uuid).filter_by(user_uuid=cls.uuid)

    @hybrid_property
    def active_sessions(self):
        return [session for session in self.sessions if session.is_active]

    @active_sessions.expression
    def active_sessions(cls):
        return sa.select(SessionModel).filter_by(user_uuid=cls.uuid, is_active=True)

    @hybrid_property
    def active_sessions_uuids(self):
        return [session.uuid for session in self.sessions if session.is_active]

    @active_sessions_uuids.expression
    def active_sessions_uuids(cls):
        return sa.select(SessionModel.uuid).filter_by(user_uuid=cls.uuid, is_active=True)

    @hybrid_property
    def permissions(self):
        permissions = []
        for role in self.roles:
            permissions.extend(role.permissions)
        return list(set(permissions))

    @permissions.expression
    def permissions(cls):
        return (
            sa.select(PermissionModel)
            .join(RolePermissionAssociation)
            .join(RoleModel)
            .join(cls.roles)
            .where(UserRoleAssociation.user_uuid == cls.uuid)
        )

    @hybrid_property
    def permissions_names(self):
        return list(set([perm.name for perm in self.permissions]))

    @permissions_names.expression
    def permissions_names(cls):
        return (
            sa.select(PermissionModel.name)
            .join(RolePermissionAssociation)
            .join(RoleModel)
            .join(cls.roles)
            .where(UserRoleAssociation.user_uuid == cls.uuid)
        )

    @hybrid_property
    def roles_names(self):
        return list(set([role.name for role in self.roles]))

    @permissions_names.expression
    def permissions_names(cls):
        return (
            sa.select(RoleModel.name)
            .join(UserRoleAssociation)
            .join(RoleModel)
            .join(cls.roles)
            .where(UserRoleAssociation.user_uuid == cls.uuid)
        )

    def __repr__(self):
        return f'<UserModel> ({self.id=:}, {self.uuid=:},{self.email=:}, {self.name=:})'
