import abc

import pydantic as pd
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from core.enums import OrderEnum
from core.exceptions import BadRequestException, UserAlreadyExistsException
from db import Base as sa_BaseModel
from db.models.user import UserModel
from db.serializers.user import UserUpdateSerializer
from services.hasher import get_password_hash


class DBRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def remove(self, *args, **kwargs):
        pass


class SqlAlchemyRepositoryAsync(DBRepository):
    def __init__(self, session: sa_async.AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def create(self, Model: type[sa_BaseModel], serializer) -> sa_BaseModel:
        serializer_data = jsonable_encoder(serializer)
        obj = Model(**serializer_data)
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while creating {Model=:}: {str(e)}')

        await self.session.refresh(obj)
        return obj

    async def validate_user_email(self, email):
        user_with_the_same_email = await self.get(UserModel, email=email)
        if user_with_the_same_email is not None:
            raise UserAlreadyExistsException

    async def create_user(self, user_serializer):
        await self.validate_user_email(user_serializer.email)
        user_serializer.password = get_password_hash(user_serializer.password)
        user = await self.create(UserModel, user_serializer)
        return user

    async def get(self, Model: type[sa_BaseModel], **kwargs) -> sa_BaseModel:
        stmt = select(Model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        return obj

    async def get_all(self, Model: type[sa_BaseModel]) -> list[sa_BaseModel]:
        stmt = select(Model)
        result = await self.session.execute(stmt)
        objs = result.scalars().all()
        return objs

    async def get_or_create_many(
            self, Model: type[sa_BaseModel], serializers: list[pd.BaseModel]
    ) -> list[sa_BaseModel]:
        objs = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            stmt = select(Model).filter_by(**serializer_data)
            result = await self.session.execute(stmt)
            obj = result.scalars().first()
            if obj is None:
                obj = Model(**serializer_data)
                self.session.add(obj)
            objs.append(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while creating {Model=:}: {str(e)}')
        return objs

    async def get_or_create_by_name(self, Model: type[sa_BaseModel], name: str) -> tuple[bool, sa_BaseModel]:
        is_created = False
        stmt = select(Model).filter_by(name=name)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        if not obj:
            obj = Model(name=name)
            self.session.add(obj)
            try:
                await self.session.commit()
            except IntegrityError as e:
                await self.session.rollback()
                raise ValueError(f'Error while creating {Model=:}: {str(e)}')
            await self.session.refresh(obj)
            is_created = True
        return is_created, obj

    async def update(self, obj: sa_BaseModel, serializer: pd.BaseModel | dict) -> sa_BaseModel:
        if isinstance(serializer, UserUpdateSerializer):
            await self.validate_user_email(serializer.email)

        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.dict(exclude_unset=True)

        # Filter out fields that should not be updated
        fields_to_update = [x for x in update_data if hasattr(obj, x)]
        for field in fields_to_update:
            setattr(obj, field, update_data[field])
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while updating {obj=:}: {str(e)}')
        await self.session.refresh(obj)
        return obj

        # obj_data = json.loads(json.dumps(obj, cls=CustomEncoder))
        # for obj_data_field in obj_data:
        #     field = obj_data_field.strip('_')
        #     if field in update_data:
        #         setattr(obj, field, update_data[field])
        # self.session.add(obj)
        # try:
        #     await self.session.commit()
        # except IntegrityError as e:
        #     await self.session.rollback()
        #     raise ValueError(f'Error while updating {obj=:}: {str(e)}')
        # await self.session.refresh(obj)
        # return obj

    async def remove(self, Model: type[sa_BaseModel], id) -> None:
        obj = await self.get(Model, id=id)
        if obj is None:
            raise BadRequestException(f'Cant remove, {Model=:} {id=:} not found')
        await self.session.delete(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while removing {Model=:} {id=:}: {str(e)}')

    def get_paginated_query(self, Model: type[sa_BaseModel], query: Query, order_by: str, order: OrderEnum,
                            pagination_params):
        order = sa.desc if order.value == 'desc' else sa.asc
        query = query.order_by(order(getattr(Model, order_by))) \
            .offset(pagination_params['offset']) \
            .limit(pagination_params['limit'])
        return query
