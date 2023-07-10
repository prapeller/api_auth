from contextlib import asynccontextmanager

import fastapi as fa
import uvicorn
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

import core.dependencies
from api.v1.authorized import auth as v1_auth_authorized
from api.v1.authorized import me as v1_me
from api.v1.authorized import postgres as v1_postgres
from api.v1.authorized import roles as v1_roles
from api.v1.public import auth as v1_auth_public
from core.config import settings
from core.dependencies import verified_token_schema_dependency
from db import init_models


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # startup
    init_models()
    core.dependencies.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    yield
    # shutdown
    await core.dependencies.redis.close()


app = fa.FastAPI(lifespan=lifespan,
                 title=settings.PROJECT_NAME,
                 docs_url=f'/{settings.DOCS_URL}',
                 openapi_url='/api/openapi.json',
                 default_response_class=ORJSONResponse,
                 )

v1_router_public = fa.APIRouter()
v1_router_public.include_router(v1_auth_public.router, prefix='/auth', tags=['auth'])

v1_router_authorized = fa.APIRouter(dependencies=[fa.Depends(verified_token_schema_dependency)])
v1_router_authorized.include_router(v1_postgres.router, prefix='/postgres', tags=['postgres'])
v1_router_authorized.include_router(v1_auth_authorized.router, prefix='/auth', tags=['auth'])
v1_router_authorized.include_router(v1_roles.router, prefix='/roles', tags=['roles'])
v1_router_authorized.include_router(v1_me.router, prefix='/me', tags=['me'])

app.include_router(v1_router_public, prefix='/api/v1')
app.include_router(v1_router_authorized, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run('main:app', host=settings.API_HOST, port=settings.API_PORT, reload=True)
