import abc
import json

import pydantic as pd
import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session

from core.enums import OrderEnum
from core.exceptions import BadRequestException
from core.shared import CustomEncoder
from db import Base as sa_BaseModel


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


class SqlAlchemyRepository(DBRepository):
    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def create(self, Model: type[sa_BaseModel], serializer) -> sa_BaseModel:
        serializer_data = jsonable_encoder(serializer)
        obj = Model(**serializer_data)
        self.session.add(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f'Error while creating {Model=:}: {str(e)}')

        self.session.refresh(obj)
        return obj

    def get(self, Model: type[sa_BaseModel], **kwargs) -> sa_BaseModel:
        obj = self.session.query(Model).filter_by(**kwargs).first()
        return obj

    def get_all(self, Model: type[sa_BaseModel]) -> list[sa_BaseModel]:
        objs = self.session.query(Model).all()
        return objs

    def get_or_create_many(self, Model: type[sa_BaseModel], serializers: list[pd.BaseModel]) -> list[sa_BaseModel]:
        objs = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            obj = self.session.query(Model).filter_by(**serializer_data).first()
            if obj is None:
                obj = Model(**serializer_data)
                self.session.add(obj)
            objs.append(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f'Error while creating {Model=:}: {str(e)}')
        return objs

    def get_or_create_by_name(self, Model: type[sa_BaseModel], name: str) -> tuple[bool, sa_BaseModel]:
        is_created = False
        obj = self.session.query(Model).filter_by(name=name).first()
        if not obj:
            obj = Model(name=name)
            self.session.add(obj)
            try:
                self.session.commit()
            except IntegrityError as e:
                self.session.rollback()
                raise ValueError(f'Error while creating {Model=:}: {str(e)}')
            self.session.refresh(obj)
            is_created = True
        return is_created, obj

    def update(self, obj: sa_BaseModel, serializer: pd.BaseModel | dict) -> sa_BaseModel:
        obj_data = json.loads(json.dumps(obj, cls=CustomEncoder))
        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.dict(exclude_unset=True)

        for obj_data_field in obj_data:
            field = obj_data_field.strip('_')
            if field in update_data:
                setattr(obj, field, update_data[field])
        self.session.add(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f'Error while updating {obj=:}: {str(e)}')
        self.session.refresh(obj)
        return obj

    def remove(self, Model: type[sa_BaseModel], id) -> None:
        obj = self.get(Model, id=id)
        if obj is None:
            raise BadRequestException(f'Cant remove, {Model=:} {id=:} not found')
        self.session.delete(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f'Error while removing {Model=:} {id=:}: {str(e)}')

    def get_paginated_query(self, Model: type[sa_BaseModel], query: Query, order_by: str, order: OrderEnum,
                            pagination_params) -> Query:
        order = sa.desc if order.value == 'desc' else sa.asc
        query = query.order_by(order(getattr(Model, order_by))) \
            .offset(pagination_params['offset']) \
            .limit(pagination_params['limit'])
        return query
