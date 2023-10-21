from contextlib import asynccontextmanager
from logging import Logger
from pathlib import Path

import fastapi as fa
import uvicorn
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from redis.asyncio import Redis

import core.dependencies
from api.v1.authorized import auth as v1_auth_authorized
from api.v1.authorized import me as v1_me
from api.v1.authorized import postgres as v1_postgres
from api.v1.authorized import roles as v1_roles
from api.v1.public import auth as v1_auth_public
from core.config import settings
from core.dependencies import verified_token_schema_dependency
from core.logger_config import setup_logger
from db import init_models

logger: Logger | None = None


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    # trace.get_tracer_provider().add_span_processor(
    #     BatchSpanProcessor(JaegerExporter(agent_host_name=settings.JAEGER_HOST, agent_port=settings.JAEGER_PORT)))
    # trace.get_tracer_provider().add_span_processor(
    #     BatchSpanProcessor(ConsoleSpanExporter()))


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # startup
    init_models()
    global logger
    SERVICE_DIR = Path(__file__).resolve().parent
    SERVICE_NAME = SERVICE_DIR.stem
    logger = setup_logger(SERVICE_NAME, SERVICE_DIR)
    core.dependencies.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    configure_tracer()
    yield
    # shutdown
    await core.dependencies.redis.close()


app = fa.FastAPI(lifespan=lifespan,
                 title=settings.PROJECT_NAME,
                 docs_url=f'/{settings.DOCS_URL}',
                 openapi_url='/api/openapi.json',
                 default_response_class=ORJSONResponse,
                 )

FastAPIInstrumentor.instrument_app(app)


@app.middleware('http')
async def log_request_id(request: fa.Request, call_next):
    request_id = request.headers.get('X-Request-Id', 'None')

    # with trace.get_tracer(__name__).start_as_current_span("main-span") as span:
    #     span.set_attribute("request_id", request_id)

    logger.info(f'Request processed: {request_id=:}', extra={'request_id': request_id})
    return await call_next(request)


v1_router_auth = fa.APIRouter(dependencies=[fa.Depends(verified_token_schema_dependency)])
v1_router_auth.include_router(v1_postgres.router, prefix='/postgres', tags=['postgres'])
v1_router_auth.include_router(v1_auth_authorized.router, prefix='/auth', tags=['auth'])
v1_router_auth.include_router(v1_roles.router, prefix='/roles', tags=['roles'])
v1_router_auth.include_router(v1_me.router, prefix='/me', tags=['me'])

v1_router_public = fa.APIRouter()
v1_router_public.include_router(v1_auth_public.router, prefix='/auth', tags=['auth'])

app.include_router(v1_router_auth, prefix='/api/v1')
app.include_router(v1_router_public, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run('main:app', host=settings.API_AUTH_HOST, port=settings.API_AUTH_PORT, reload=True)
