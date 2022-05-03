import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from adapters.repository import SQLAlchemyRepository
from service_layer.queue.producer import start_producer
from service_layer.tasks import send_to_consumer, start_parse


log = logging.getLogger(__name__)
logging.basicConfig(format="[%(asctime)s: %(levelname)s] %(message)s")
log.setLevel(logging.DEBUG)


async def start_sync(db_session: AsyncSession):
    repository = SQLAlchemyRepository(db_session)
    producer = await start_producer()
    data = await asyncio.gather(*[start_parse(position.name) for position in await repository.get_positions()])

    tasks = list()
    for item in data:
        for key, vacancies in item.items():
            log.info(f"Found {len(vacancies)} vacancies for {key[1]}")
            for vacancy in vacancies:
                task = asyncio.create_task(send_to_consumer(producer, key.parser_class, key.position_name, vacancy))
                tasks.append(task)

    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    await producer.stop()
