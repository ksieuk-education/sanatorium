"""
Утилиты для работы с sqlalchemy
"""
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_asyncio


async def execute_sql_text(
    async_session: sa_asyncio.async_sessionmaker[sa_asyncio.AsyncSession],
    func_text: str,
) -> sqlalchemy.Result[typing.Any]:
    """
    Асинхронное выполнение произвольной функции базы данных

    :param async_session: Асинхронная сессия базы данных для выполнения запроса
    :param func_text: Текст функции для выполнения
    :param is_many_scalar_response: Нужно ли получить .scalars(), вместо .scalar()
    :return: Результат выполнения функции
    """

    async with async_session() as session, session.begin():
        query = sqlalchemy.text(func_text)
        return await session.execute(query)
