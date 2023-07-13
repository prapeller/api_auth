import asyncio

from core.enums import RolesNamesEnum, PermissionsNamesEnum
from db import SessionLocalAsync, init_models
from db.models.permission import PermissionModel
from db.models.role import RoleModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.permission import PermissionCreateSerializer


async def create_permissions_all():
    permission_ser_list = []
    for perm_name in PermissionsNamesEnum:
        permission_ser_list.append(PermissionCreateSerializer(name=perm_name))
    async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
        await repo.get_or_create_many(PermissionModel, permission_ser_list)


async def create_roles_all():
    async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
        for role_name in RolesNamesEnum:
            if role_name == RolesNamesEnum.superuser:
                is_created, superuser_role = await repo.get_or_create_by_name(RoleModel, role_name)
                is_created, all_of_all_perm = await repo.get_or_create_by_name(PermissionModel,
                                                                               PermissionsNamesEnum.all_of_all)
                superuser_role.permissions.append(all_of_all_perm)

            if role_name == RolesNamesEnum.staff:
                pass
            if role_name == RolesNamesEnum.guest:
                pass
            if role_name == RolesNamesEnum.registered:
                is_created, registered_role = await repo.get_or_create_by_name(RoleModel, role_name)
                read_users = await repo.get(PermissionModel, name=PermissionsNamesEnum.read_users)
                read_content_free = await repo.get(PermissionModel, name=PermissionsNamesEnum.read_content_free)
                read_ratings = await repo.get(PermissionModel, name=PermissionsNamesEnum.read_ratings)
                create_ratings = await repo.get(PermissionModel, name=PermissionsNamesEnum.create_ratings)
                create_comments = await repo.get(PermissionModel, name=PermissionsNamesEnum.create_comments)
                read_comments_all = await repo.get(PermissionModel, name=PermissionsNamesEnum.read_comments_all)
                update_comments_my = await repo.get(PermissionModel, name=PermissionsNamesEnum.update_comments_my)
                registered_role.permissions.extend([read_users, read_content_free, read_ratings, create_ratings,
                                                    create_comments, read_comments_all, update_comments_my])
            if role_name == RolesNamesEnum.premium:
                pass

            await repo.session.commit()


async def create_roles_and_permissions():
    await create_permissions_all()
    await create_roles_all()


if __name__ == '__main__':
    init_models()
    asyncio.run(create_roles_and_permissions())
