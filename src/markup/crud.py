import uuid
import typing as tp
import datetime as dt
from pprint import pprint

import asyncpg
from src.markup import schemas as sch   


async def create_research(con: asyncpg.Connection, creator_id: int, name: str, description: str, tags: tp.List[str]) -> str:
    '''
    Создание записи с информацией об исследовании
    '''
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


async def create_task(con: asyncpg.Connection, research_id: str, user_id: int, deadline: dt.datetime) -> asyncpg.Record:
    '''
    Создание задачи
    '''
    query = '''
    INSERT INTO tasks (research_id, user_id, deadline) VALUES ($1, $2, $3) RETURNING id, created_at, status;
    '''
    return await con.fetchrow(query, research_id, user_id, deadline)


async def have_access_to_research(con: asyncpg.Connection, user_id: int, research_id: tp.Union[str, uuid.UUID]) -> bool:
    '''
    Проверка наличия доступа пользователя к исследованию (имеет, если является модератором или имеет задачу по работе с иссл.)
    '''
    query = '''
    SELECT EXISTS (
        SELECT 1 FROM researches r
        LEFT JOIN tasks
        ON
        r.id = tasks.research_id 
        WHERE 
        (r.id = $2 AND r.creator_id = $1)
        OR 
        (tasks.research_id = $2 AND tasks.marker_id = $1)
        );
    '''
    return await con.fetchval(query, user_id, research_id)


async def get_tags(con: asyncpg.Connection) -> tp.List[str]:
    '''
    Получение списка имеющихся тегов
    '''
    query = '''
    SELECT name FROM tags;
    '''
    res = await con.fetch(query)
    return [row['name'] for row in res]


async def add_tags(con: asyncpg.Connection, tags: tp.List[str]):
    '''
    Добавление тега
    '''
    query = '''
    INSERT INTO tags (name) VALUES ($1) ON CONFLICT DO NOTHING;
    '''
    await con.executemany(query, [(tag,) for tag in tags])


async def get_markers(con: asyncpg.Connection) -> tp.List[sch.Marker]:
    '''
    Получение списка разметчиков
    '''
    query = '''
    SELECT id, surname, name, patronymic FROM users
    WHERE role = 'marker';
    '''
    res = await con.fetch(query)
    return [sch.Marker.parse_obj(row) for row in res]


async def change_task_status(con: asyncpg.Connection, research_id: str, status: sch.TaskStatus):
    '''
    Изменение статуса задачи
    '''
    query = '''
    UPDATE tasks SET status = $2 WHERE id = $1 RETURNING id;
    '''
    res = await con.fetchval(query, research_id, status)
    
    
async def search_tasks(con: asyncpg.Connection, 
                       research_name: tp.Optional[str], 
                       status: tp.Optional[str], 
                       user_id: tp.Optional[int]):
    '''
    Поиск по задачам с фильтрами по:
    - наименованию исследования
    - статусу
    - назначенному пользователю (разметчику)
    '''
    research_name_filter = '''
    r.name ILIKE '%' || ${} || '%'
    '''
    status_filter = '''
    t.status = ${}
    '''
    user_id_filter = '''
    u.id = ${}
    '''
    filters = []
    query_args = []
    filters_count = 0
    if research_name is not None:
        filters_count += 1
        filters.append(research_name_filter.format(filters_count))
        query_args.append(research_name)
        
    if status is not None:
        filters_count += 1
        filters.append(status_filter.format(filters_count))
        query_args.append(status)
        
    if user_id is not None:
        filters_count += 1
        filters.append(user_id_filter.format(filters_count))
        query_args.append(int(user_id))
    
    where_clause = 'WHERE ' + ' AND '.join(filters) if filters else ''
    query = f'''
    SELECT 
    t.id as "task_id",
    r.id as "research_id",
    u.id as "user_id",
    u.name as "user_name",
    u.surname as "user_surname",
    u.patronymic as "user_patronymic",
    t.deadline as "task_deadline",
    t.created_at as "task_created_at",
    t.status as "task_status"
    FROM
    tasks t 
    LEFT JOIN users u ON t.user_id = u.id
    LEFT JOIN researches r ON t.research_id = r.id
    {where_clause};
    '''
    return await con.fetch(query, *query_args)

    
    
async def search_researches(con: asyncpg.Connection, search_query: tp.Optional[str], tags: tp.Optional[tp.List[str]]):
    '''
    Поиск по исследованиям с фильтром по тегам
    '''
    tags_filter = '''
    ${} <@ (array(SELECT name 
              FROM researches_tags r_t
              LEFT JOIN tags t ON t.id = r_t.tag_id
              WHERE r_t.research_id = r.id
              ))
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
        
    if search_query is not None:
        filters_count += 1
        filters.append(research_name_filter.format(filters_count))
        query_args.append(search_query)
        
    
    where_clause = 'WHERE ' + ' AND '.join(filters) if filters else ''
    
    query = f'''
    SELECT
    r.id as "id", 
    r.name as "name", 
    r.description as "description",
    (SELECT count(*) FROM tasks WHERE research_id = r.id) as "tasks_count",
    array(SELECT name 
          FROM researches_tags r_t
          LEFT JOIN tags t ON t.id = r_t.tag_id
          WHERE r_t.research_id = r.id
          ) as "tags"
    FROM researches r
    LEFT JOIN researches_tags r_t ON r_t.research_id = r.id
    LEFT JOIN tags t ON t.id = r_t.tag_id
    LEFT JOIN tasks ON r.id = tasks.research_id 
    {where_clause}
    GROUP BY r.id;    
    '''
    
    return await con.fetch(query, *query_args)