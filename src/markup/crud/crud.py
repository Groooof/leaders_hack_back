import uuid
import typing as tp
from pprint import pprint

import asyncpg
from src.markup import schemas as sch   


async def create_research(con: asyncpg.Connection, creator_id: int, name: str, description: str, tags: tp.List[str]) -> str:
    query_research = '''
    INSERT INTO researches (creator_id, name, description) VALUES ($1, $2, $3) RETURNING id;
    '''
    query_tags = '''
    INSERT INTO researches_tags (research_id, tag_id)  
    SELECT $1, id FROM tags WHERE name = $2;
    '''

    async with con.transaction():
        research_id = await con.fetchval(query_research, creator_id, name, description)
        research_id = str(research_id)
        for tag in tags:
            await con.execute(query_tags, research_id, tag)
    return research_id


async def have_access_to_research(con: asyncpg.Connection, user_id: int, research_id: tp.Union[str, uuid.UUID]) -> bool:
    query = '''
    SELECT EXISTS (
        SELECT 1 FROM researches r
        LEFT JOIN researches_markers r_m
        ON
        r.id = r_m.research_id 
        WHERE 
        (r.id = $2 AND r.creator_id = $1)
        OR 
        (r_m.research_id = $2 AND r_m.marker_id = $1)
        );
    '''
    return await con.fetchval(query, user_id, research_id)


async def get_tags(con: asyncpg.Connection) -> tp.List[str]:
    query = '''
    SELECT name FROM tags;
    '''
    res = await con.fetch(query)
    return [row['name'] for row in res]


async def add_tags(con: asyncpg.Connection, tags: tp.List[str]):
    query = '''
    INSERT INTO tags (name) VALUES ($1) ON CONFLICT DO NOTHING;
    '''
    await con.executemany(query, [(tag,) for tag in tags])


async def get_markers(con: asyncpg.Connection) -> tp.List[sch.Marker]:
    query = '''
    SELECT id, surname, name, patronymic FROM users
    WHERE role = 'marker';
    '''
    res = await con.fetch(query)
    return [sch.Marker.parse_obj(row) for row in res]


async def change_research_status(con: asyncpg.Connection, research_id: str, status: sch.ResearchStatus):
    query = '''
    UPDATE researches SET status = $2 WHERE id = $1 RETURNING id;
    '''
    res = await con.fetchval(query, research_id, status)
    
    
async def search(con: asyncpg.Connection, search_query: tp.Optional[str], tags: tp.Optional[tp.List[str]], marker_id: tp.Optional[int]):
    tags_filter = '''
    ${} <@ (array(SELECT name 
              FROM researches_tags r_t
              LEFT JOIN tags t ON t.id = r_t.tag_id
              WHERE r_t.research_id = r.id
              ))
    '''
    marker_filter = '''
    u.id = ${}
    '''
    research_name_filter = '''
    r.name ILIKE '%' || ${} || '%'
    '''
    filters = []
    query_args = []
    filters_count = 0
    if tags is not None:
        filters_count += 1
        filters.append(tags_filter.format(filters_count))
        query_args.append(tags)
        
    if marker_id is not None:
        filters_count += 1
        filters.append(marker_filter.format(filters_count))
        query_args.append(marker_id)
        
    if search_query is not None:
        filters_count += 1
        filters.append(research_name_filter.format(filters_count))
        query_args.append(search_query)
        
    
    where_clause = 'WHERE ' + ' AND '.join(filters) if filters else ''
    
    query = f'''
    SELECT 
    r.id as "research_id", 
    r.name as "research_name", 
    r.description as "research_description",
    r.status as "research_status",
    u.id as "marker_id", 
    u.name as "marker_name", 
    u.surname as "marker_surname", 
    u.patronymic as "marker_patronymic",
    array(SELECT name 
          FROM researches_tags r_t
          LEFT JOIN tags t ON t.id = r_t.tag_id
          WHERE r_t.research_id = r.id
          ) as research_tags 
    FROM researches_tags r_t
    LEFT JOIN researches as "r" ON r.id = r_t.research_id 
    LEFT JOIN tags t ON t.id = r_t.tag_id
    LEFT JOIN researches_markers r_m ON r.id = r_m.research_id 
    LEFT JOIN users u ON u.id = r_m.marker_id
    {where_clause}
    GROUP BY r.id, u.id;
    '''
    return await con.fetch(query, *query_args)