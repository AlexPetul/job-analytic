import asyncio
import aiohttp
import logging

from bs4 import BeautifulSoup
from collections import defaultdict
from typing import List

from job_analytic.adapters.repository import SQLAlchemyRepository
from job_analytic.db.config import SessionLocal
from job_analytic.service_layer.parsers.abstract import BaseParser
from job_analytic.service_layer.parsers.rabota_by.main import RabotaByParser
from job_analytic.service_layer.queue.producer import start_producer

MAX_SIM_WORKERS = 50
parser_classes = [RabotaByParser()]

log = logging.getLogger(__name__)
logging.basicConfig(format="[%(asctime)s: %(levelname)s] %(message)s")
log.setLevel(logging.DEBUG)


async def get_initial_search_page(parser: BaseParser, position_name: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        response = await session.get("{base_url}{search}".format(
            base_url=parser.base_url,
            search=parser.get_interpolated_query_param(position_name)
        ))
        content = await response.read()
    return BeautifulSoup(content.decode(), "html5lib")


async def get_page_with_vacancies(parser: BaseParser, page: int, position_name: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        response = await session.get("{base_url}{search}&page={page}".format(
            base_url=parser.base_url,
            search=parser.get_interpolated_query_param(position_name),
            page=page
        ))
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
            vacancies[(parser, position_name)].extend(parser.get_vacancies(page_content))
    return vacancies


async def fetch_worker(queue: asyncio.Queue):
    async with aiohttp.ClientSession() as session:
        while True:
            queue_item = await queue.get()
            try:
                if queue_item is None:
                    return

                skills = await get_skills(
                    session=session,
                    parser=queue_item["parser"],
                    vacancy_link=queue_item["vacancy"]
                )
                await queue_item["producer"].send("jobs", key=queue_item["position_name"], value=skills)
            finally:
                queue.task_done()


async def start_sync():
    repository = SQLAlchemyRepository(SessionLocal())
    producer = await start_producer()
    data = await asyncio.gather(*[start_parse(position.name) for position in repository.list_positions()])

    queue = asyncio.Queue()
    worker_tasks = list()
    for _ in range(MAX_SIM_WORKERS):
        worker_tasks.append(asyncio.create_task(coro=fetch_worker(queue=queue)))

    for item in data:
        for parser, vacancies in item.items():
            log.info(f"Found {len(vacancies)} vacancies for {parser[1]}")
            for vacancy in vacancies:
                await queue.put(dict(
                    parser=parser[0],
                    position_name=parser[1],
                    vacancy=vacancy,
                    producer=producer
                ))

    for _ in range(MAX_SIM_WORKERS):
        await queue.put(None)

    await queue.join()
    await asyncio.wait(worker_tasks)
