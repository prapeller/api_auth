import fastapi as fa

from core.dependencies import sql_alchemy_repo_dependency
from core.enums import PermissionsNamesEnum, ResponseDetailEnum
from core.security import permissions
from db.models.role import RoleModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.role import RoleReadSerializer, RoleUpdateSerializer

router = fa.APIRouter()


@router.get("/",
            response_model=list[RoleReadSerializer])
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def roles_list(
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
):
    return await repo.get_all(RoleModel)


@router.put("/{id}",
            response_model=RoleReadSerializer)
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def roles_update(
        id: str,
        role_ser: RoleUpdateSerializer,
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
):
    role = await repo.get(RoleModel, id=id)
    role = await repo.update(role, role_ser)
    return role


@router.delete("/{id}")
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def roles_delete(
        id: str,
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
):
    await repo.remove(RoleModel, id)
    return {'detail': ResponseDetailEnum.ok}
