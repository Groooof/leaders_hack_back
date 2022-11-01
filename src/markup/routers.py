import asyncpg
from fastapi import APIRouter, Depends

from src.auth import backends
from src.dependencies import get_db_connection
from src.markup import crud
from src.schemas import Error


router = APIRouter(prefix='/api/v1', tags=['assistant'])
router.responses = {403: {'description': 'Access denied', 'model': Error},
                    401: {'description': 'Token expired', 'model': Error}}


@router.get('/get_admin', dependencies=[Depends(backends.jwt_auth),
                                        Depends(backends.is_superuser)])
async def get_admin(con: asyncpg.Connection = Depends(get_db_connection)):

    return await crud.get_admin(con)

    
    


