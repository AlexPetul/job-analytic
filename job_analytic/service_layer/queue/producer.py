import json

from aiokafka import AIOKafkaProducer

from core.settings import settings


async def start_producer():
    producer = AIOKafkaProducer(
        acks=1,
        client_id="job-analytic-producer",
        bootstrap_servers=settings["KAFKA"]["Host"],
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    return producer
