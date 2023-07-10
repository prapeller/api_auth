from core.enums import RolesNamesEnum, PermissionsNamesEnum
from db import SessionLocal, init_models
from db.models.permission import PermissionModel
from db.models.role import RoleModel
from db.repository import SqlAlchemyRepository
from db.serializers.permission import PermissionCreateSerializer


def create_permissions_all():
    permission_ser_list = []
    for perm_name in PermissionsNamesEnum:
        permission_ser_list.append(PermissionCreateSerializer(name=perm_name))
    with SqlAlchemyRepository(SessionLocal()) as repo:
        repo.get_or_create_many(PermissionModel, permission_ser_list)


def create_roles_all():
    create_permissions_all()

    with SqlAlchemyRepository(SessionLocal()) as repo:
        for role_name in RolesNamesEnum:
            if role_name == RolesNamesEnum.superuser:
                is_created, superuser_role = repo.get_or_create_by_name(RoleModel, role_name)
                is_created, all_of_all_perm = repo.get_or_create_by_name(PermissionModel,
                                                                         PermissionsNamesEnum.all_of_all)
                superuser_role.permissions.append(all_of_all_perm)

            if role_name == RolesNamesEnum.staff:
                pass
            if role_name == RolesNamesEnum.guest:
                pass
            if role_name == RolesNamesEnum.registered:
                is_created, registered_role = repo.get_or_create_by_name(RoleModel, role_name)
                read_users = repo.get(PermissionModel, name=PermissionsNamesEnum.read_users)
                read_content_free = repo.get(PermissionModel, name=PermissionsNamesEnum.read_content_free)
                read_ratings = repo.get(PermissionModel, name=PermissionsNamesEnum.read_ratings)
                create_ratings = repo.get(PermissionModel, name=PermissionsNamesEnum.create_ratings)
                create_comments = repo.get(PermissionModel, name=PermissionsNamesEnum.create_comments)
                read_comments_all = repo.get(PermissionModel, name=PermissionsNamesEnum.read_comments_all)
                update_comments_my = repo.get(PermissionModel, name=PermissionsNamesEnum.update_comments_my)
                registered_role.permissions.extend([read_users, read_content_free, read_ratings, create_ratings,
                                                    create_comments, read_comments_all, update_comments_my])
            if role_name == RolesNamesEnum.premium:
                pass

            repo.session.commit()


if __name__ == '__main__':
    init_models()
    create_roles_all()
