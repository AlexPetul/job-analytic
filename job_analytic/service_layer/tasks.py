from collections import defaultdict, namedtuple
from typing import List

import aiohttp
from aiokafka import AIOKafkaProducer
from bs4 import BeautifulSoup

from core.settings import settings
from service_layer.parsers.abstract import BaseParser
from service_layer.parsers.rabota_by.main import RabotaByParser
from service_layer.resources.pool import ResourcePool


parser_classes = [RabotaByParser()]


async def get_initial_search_page(parser: BaseParser, position_name: str) -> BeautifulSoup:
    session = await ResourcePool().http_session
    response = await session.get(
        "{base_url}{search}".format(base_url=parser.base_url, search=parser.get_interpolated_query_param(position_name))
    )
    content = await response.read()
    return BeautifulSoup(content.decode(), "html5lib")


async def get_page_with_vacancies(parser: BaseParser, page: int, position_name: str) -> BeautifulSoup:
    session = await ResourcePool().http_session
    response = await session.get(
        "{base_url}{search}&page={page}".format(
            base_url=parser.base_url, search=parser.get_interpolated_query_param(position_name), page=page
        )
    )
    content = await response.read()
    return BeautifulSoup(content.decode(), "html5lib")


async def get_skills(session: aiohttp.ClientSession, parser: BaseParser, vacancy_link: str) -> List[str]:
    response = await session.get(vacancy_link)
    content = await response.read()
    soup = BeautifulSoup(content.decode(), "html5lib")
    return parser.get_skills(soup)


async def start_parse(position_name: str) -> defaultdict[BaseParser, List[str]]:
    vacancies = defaultdict(list)
    for parser in parser_classes:
        start_page = await get_initial_search_page(parser, position_name)
        pages = parser.get_page_count(start_page)

        for page in range(pages):
            page_content = await get_page_with_vacancies(parser, page, position_name)
            ParserContext = namedtuple("ParserContext", "parser_class, position_name")
            key = ParserContext(parser_class=parser, position_name=position_name)
            vacancies[key].extend(parser.get_vacancies(page_content))
    return vacancies


async def send_to_consumer(producer: AIOKafkaProducer, parser: BaseParser, position_name: str, vacancy: str):
    session = await ResourcePool().http_session
    skills = await get_skills(session=session, parser=parser, vacancy_link=vacancy)
    await producer.send(settings["KAFKA"]["Host"], key=position_name, value=skills)
