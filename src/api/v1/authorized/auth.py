import fastapi as fa

from core.dependencies import auth_manager_dependency, verified_access_token_dependency
from core.enums import ResponseDetailEnum
from services.auth_manager import AuthManager

router = fa.APIRouter()


@router.post("/logout",
             responses={
                 fa.status.HTTP_200_OK: {'detail': ResponseDetailEnum.ok},
                 fa.status.HTTP_401_UNAUTHORIZED: {'detail': ResponseDetailEnum.unauthorized},
             })
async def auth_logout(
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
        access_token: str = fa.Depends(verified_access_token_dependency),
):
    await auth_manager.logout(access_token)
    return {'detail': ResponseDetailEnum.ok}


@router.post("/logout-all",
             responses={
                 fa.status.HTTP_200_OK: {'detail': ResponseDetailEnum.ok},
                 fa.status.HTTP_401_UNAUTHORIZED: {'detail': ResponseDetailEnum.unauthorized},
             })
async def auth_logout_all(
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
        access_token: str = fa.Depends(verified_access_token_dependency),
):
    await auth_manager.logout_all(access_token)
    return {'detail': ResponseDetailEnum.ok}
