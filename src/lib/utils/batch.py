"""
Утилиты для работы с итерируемыми объектами
"""

import itertools
import typing


def get_chunk(
    request: typing.Iterable[typing.Any],
    chunk_size: int,
) -> typing.Generator[list[typing.Any], None, None]:
    """
    Генератор для разделения итерируемого объекта на части

    :param request: Итерируемый объект
    :param chunk_size: Размер одной части
    :return: Части итерируемого объекта
    """

    request_iterator = iter(request)
    while chunk := list(itertools.islice(request_iterator, chunk_size)):
        yield chunk


def get_mono_list(
    request: typing.Sequence[typing.Sequence[typing.Any]],
) -> list[typing.Any]:
    """
    Создание одномерного списка из двумерного

    :param request: Двумерный список
    :return: Одномерный список
    """

    result: list[typing.Any] = []
    for item_list in request:
        result.extend(item_list)
    return result
