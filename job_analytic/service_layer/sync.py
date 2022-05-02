import asyncio
import logging

from job_analytic.adapters.repository import SQLAlchemyRepository
from job_analytic.db.config import SessionLocal
from job_analytic.service_layer.queue.producer import start_producer
from job_analytic.service_layer.tasks import send_to_consumer, start_parse


log = logging.getLogger(__name__)
logging.basicConfig(format="[%(asctime)s: %(levelname)s] %(message)s")
log.setLevel(logging.DEBUG)


async def start_sync():
    repository = SQLAlchemyRepository(SessionLocal())
    producer = await start_producer()
    data = await asyncio.gather(*[start_parse(position.name) for position in repository.get_positions()])

    tasks = list()
    for item in data:
        for parser, vacancies in item.items():
            log.info(f"Found {len(vacancies)} vacancies for {parser[1]}")
            for vacancy in vacancies:
                task = asyncio.create_task(send_to_consumer(producer, parser[0], parser[1], vacancy))
                tasks.append(task)

    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    await producer.stop()
