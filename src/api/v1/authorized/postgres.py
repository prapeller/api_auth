import os
import subprocess

import fastapi as fa

from core.dependencies import verified_access_token_dependency
from core.enums import EnvEnum, PermissionsNamesEnum
from core.security import permissions

router = fa.APIRouter()


@router.post("/dump", status_code=fa.status.HTTP_201_CREATED)
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def postgres_dump(
        access_token: str = fa.Depends(verified_access_token_dependency),
        env: EnvEnum = EnvEnum.local,
):
    script_path = f"{os.getcwd()}/scripts/postgres/dump.sh"
    assert os.path.isfile(script_path)
    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'ENV': env})
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/check-dumps")
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def postgres_check_dumps(
        access_token: str = fa.Depends(verified_access_token_dependency),
):
    script_path = f"{os.getcwd()}/scripts/postgres/check_dumps.sh"
    assert os.path.isfile(script_path)
    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/download-last-dump")
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def postgres_download_last_dump(
        access_token: str = fa.Depends(verified_access_token_dependency),
):
    file_path = f"{os.getcwd()}/staticfiles/backups/dump_last"
    assert os.path.isfile(file_path)
    headers = {'Content-Disposition': 'attachment',
               'Content-Type': 'application/octet-stream'}
    return fa.responses.FileResponse(path=file_path, headers=headers, filename='dump_last')


@router.post("/restore-from-dump", status_code=fa.status.HTTP_201_CREATED)
@permissions(required=[PermissionsNamesEnum.all_of_all])
async def postgres_restore_from_dump(
        dump_file: fa.UploadFile,
        env: EnvEnum = EnvEnum.local,
        access_token: str = fa.Depends(verified_access_token_dependency),
):
    script_path = f"{os.getcwd()}/scripts/postgres/restore_from_dump.sh"
    assert os.path.isfile(script_path)

    contents = await dump_file.read()
    uploaded_file_path = 'staticfiles/backups/uploaded_dump'
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    subprocess.Popen(script_path, env={'ENV': env})
    return {'message': 'ok'}
