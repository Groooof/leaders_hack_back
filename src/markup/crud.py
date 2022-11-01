import asyncpg
import typing as tp
from src.auth import schemas as sch


async def get_admin(con: asyncpg.Connection) -> tp.Optional[str]:
    query = '''
    SELECT login FROM credentials WHERE is_superuser IS TRUE;
    '''
    res = await con.fetchval(query)
    return res
    
    
    