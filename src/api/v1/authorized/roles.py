import fastapi as fa

from core.dependencies import sql_alchemy_repo_dependency
from core.enums import PermissionsNamesEnum, ResponseDetailEnum
from core.security import permissions
from db.models.role import RoleModel
from db.repository import SqlAlchemyRepository
from db.serializers.role import RoleReadSerializer, RoleUpdateSerializer

router = fa.APIRouter()


@router.get("/",
            response_model=list[RoleReadSerializer])
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def roles_list(
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
):
    return repo.get_all(RoleModel)


@router.put("/{id}",
            response_model=RoleReadSerializer)
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def roles_update(
        id: str,
        role_ser: RoleUpdateSerializer,
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
):
    role = repo.get(RoleModel, id=id)
    role = repo.update(role, role_ser)
    return role


@router.delete("/{id}")
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def roles_delete(
        id: str,
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
):
    repo.remove(RoleModel, id)
    return {'detail': ResponseDetailEnum.ok}
