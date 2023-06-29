import sqlalchemy as sa


class IdentifiedCreatedUpdated:
    id = sa.Column(sa.UUID(as_uuid=False), primary_key=True, server_default=sa.text("uuid_generate_v4()"),
                   unique=True, index=True, nullable=False)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, onupdate=sa.func.current_timestamp(), nullable=True)
