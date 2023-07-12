import pydantic as pd

from core.enums import RolesNamesEnum
from db import init_models, SessionLocalAsync
from db.models.role import RoleModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.user import UserCreateSerializer
from scripts.create_permissions_roles import create_roles_all


def create_superuser():
    init_models()

    await create_roles_all()
    while True:
        name = str(input('enter superuser name >>> '))
        email = str(input('enter superuser email >>> '))
        password = str(input('enter superuser password >>> '))
        try:
            superuser_ser = UserCreateSerializer(name=name, email=email, password=password, is_active=True)
            with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
                superuser = await superuser_ser.create(repo)
                is_created, superuser_role = await repo.get_or_create_by_name(RoleModel, RolesNamesEnum.superuser)
                superuser.roles.append(superuser_role)
                await repo.session.commit()
                await repo.session.refresh(superuser)
                print(f'Successfully created {superuser=:}')
                break
        except pd.ValidationError as e:
            print(e)


if __name__ == '__main__':
    create_superuser()
