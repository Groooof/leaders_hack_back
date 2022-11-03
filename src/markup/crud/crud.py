import uuid
import typing as tp
import asyncpg


async def create_research(con: asyncpg.Connection, creator_id: int) -> str:
    query = '''
    INSERT INTO researches (creator_id) VALUES ($1) RETURNING id;
    '''
    creator_id = await con.fetchval(query, creator_id)
    return str(creator_id)


async def have_access_to_markup(con: asyncpg.Connection, user_id: int, research_id: tp.Union[str, uuid.UUID]) -> bool:
    query = '''
    SELECT EXISTS (
        SELECT 1 FROM researches r, researches__markers r_m
        WHERE 
        (r.id = $2 AND r.creator_id = $1)
        OR 
        (r_m.research_id = $2 AND r_m.marker_id = $1)
        );
    '''
    return await con.fetchval(query, user_id, research_id)
