import sqlalchemy as sa

from db import Base


class UserRoleAssociation(Base):
    __tablename__ = 'user_role'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('role.id', ondelete='CASCADE'))

    __table_args__ = (
        sa.UniqueConstraint(
            'user_id', 'role_id', name='unique_user_id_role_id'),
        {'extend_existing': True},
    )


class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission'
    id = sa.Column(sa.Integer, primary_key=True)
    role_id = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('role.id', ondelete='CASCADE'))
    permission_id = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('permission.id', ondelete='CASCADE'))

    __table_args__ = (
        sa.UniqueConstraint(
            'role_id', 'permission_id', name='unique_role_id_permission_id'),
        {'extend_existing': True},
    )
