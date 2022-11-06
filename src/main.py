from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src import events
from src.markup.routers import router as markup_router
from src.auth.routers import router as auth_router
from src.patologies_generation.routers import router as generation_router
from src.exception_handlers import validation_error_handler, custom_http_exception_handler
from src.exceptions import CustomHTTPException
from src.utils.openapi import CustomOpenAPIGenerator


def get_app() -> FastAPI:
    """
    Инициализация и настройка объекта приложения fastapi.
    :return: объект FastAPI
    """
    app = FastAPI()
    app.title = 'Сервис для разметки снимков КТ и искусственной генерации патологий методами ИИ '
    app.description = ''
    app.version = '1.0.0'
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
    app.include_router(router=markup_router)
    app.include_router(router=auth_router)
    app.include_router(router=generation_router)
    app.add_event_handler('startup', events.on_startup)
    app.add_event_handler('shutdown', events.on_shutdown)
    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.openapi = CustomOpenAPIGenerator(app)
    return app


app = get_app()