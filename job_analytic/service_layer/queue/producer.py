import json

from aiokafka import AIOKafkaProducer


async def start_producer():
    producer = AIOKafkaProducer(
        acks=1,
        client_id="job-analytic-producer",
        bootstrap_servers="192.168.1.7:19092",
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    await producer.start()
    return producer
