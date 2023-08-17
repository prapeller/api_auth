from core.enums import RolesNamesEnum
from db import SessionLocalAsync
from db.models.role import RoleModel
from db.models.user import UserModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.user import UserCreateSerializer

user_data = {'email': 'test@mail.ru',
             'name': 'Test Name',
             'password': 'test_password123',
             'is_active': True}


async def create_test_registered_user(user_data) -> UserModel:
    async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
        user_ser = UserCreateSerializer(**user_data)
        user = await repo.get(UserModel, email=user_data['email'])
        if user is None:
            user = await repo.create_user(user_ser)
        registered_role = await repo.get(RoleModel, name=RolesNamesEnum.registered)
        user.roles.append(registered_role)
        await repo.session.commit()
        await repo.session.refresh(user)
        return user


async def delete_user_by_email(email) -> None:
    async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
        user = await repo.get(UserModel, email=email)
        if user is not None:
            await repo.remove(UserModel, id=user.id)


async def get_json_headers():
    return {
        'X-Request-Id': 'test',
        'Accept': 'application/json',
    }


async def get_login_headers():
    headers = await get_json_headers()
    headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
    return headers


async def get_login_form_data(user_data):
    form_data = {
        'username': user_data['email'],
        'password': user_data['password'],
    }
    return form_data
