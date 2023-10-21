import sqlalchemy as sa

from db import Base


class UserRoleAssociation(Base):
    __tablename__ = 'user_role'
    id = sa.Column(sa.Integer, primary_key=True)
    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'))
    role_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('role.uuid', ondelete='CASCADE'))

    __table_args__ = (
        sa.UniqueConstraint(
            'user_uuid', 'role_uuid', name='unique_user_uuid_role_uuid'),
        {'extend_existing': True},
    )


class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission'
    id = sa.Column(sa.Integer, primary_key=True)
    role_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('role.uuid', ondelete='CASCADE'))
    permission_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('permission.uuid', ondelete='CASCADE'))

    __table_args__ = (
        sa.UniqueConstraint(
            'role_uuid', 'permission_uuid', name='unique_role_uuid_permission_uuid'),
        {'extend_existing': True},
    )
