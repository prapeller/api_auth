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
    roles = relationship('RoleModel', secondary='user_role', back_populates='users')
    # many-to-one
    sessions = relationship('SessionModel', back_populates='user')
    social_accounts = relationship('SocialAccountModel', back_populates='user')

    @hybrid_property
    def roles_ids(self):
        return [role.id for role in self.roles]

    @roles_ids.expression
    def roles_ids(cls):
        return sa.select(UserRoleAssociation.role_id).filter_by(user_id=cls.id)

    @hybrid_property
    def permissions_ids(self):
        return [perm.id for perm in self.permissions]

    @permissions_ids.expression
    def permissions_ids(cls):
        return (sa.select(PermissionModel.id)
                .join(RolePermissionAssociation)
                .join(RoleModel)
                .join(cls.roles)
                .where(UserRoleAssociation.user_id == cls.id)
                )

    @hybrid_property
    def sessions_ids(self):
        return [session.id for session in self.sessions]

    @sessions_ids.expression
    def sessions_ids(cls):
        return sa.select(SessionModel.id).filter_by(user_id=cls.id)

    @hybrid_property
    def active_sessions(self):
        return [session for session in self.sessions if session.is_active]

    @active_sessions.expression
    def active_sessions(cls):
        return sa.select(SessionModel).filter_by(user_id=cls.id, is_active=True)

    @hybrid_property
    def active_sessions_ids(self):
        return [session.id for session in self.sessions if session.is_active]

    @active_sessions_ids.expression
    def active_sessions_ids(cls):
        return sa.select(SessionModel.id).filter_by(user_id=cls.id, is_active=True)

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
            .where(UserRoleAssociation.user_id == cls.id)
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
            .where(UserRoleAssociation.user_id == cls.id)
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
            .where(UserRoleAssociation.user_id == cls.id)
        )

    def __repr__(self):
        return f"<UserModel> ({self.id=:}, {self.email=:}, {self.name=:}, {self.roles=:}, {self.sessions=:})"
