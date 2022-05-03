import json
import logging
from typing import Dict, List

import aioredis
from aiokafka import AIOKafkaConsumer, ConsumerRebalanceListener
from aioredis import Redis
from kafka import TopicPartition

from adapters.repository import SQLAlchemyRepository
from core.settings import settings
from db.config import get_session
from domain import models


log = logging.getLogger(__name__)


class AIOKafkaConsumerWrapper(AIOKafkaConsumer):
    def __init__(self, redis_db: int, redis_url: str, topics: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_offset: Dict[TopicPartition, int] = {}
        self._storage: Redis = aioredis.from_url(url=redis_url, encoding="utf-8", decode_responses=True, db=redis_db)
        self._topics = topics

    def subscribe_and_set_rebalancer(self):
        class SafeRebalancerListener(ConsumerRebalanceListener):
            def __init__(self, consumer: AIOKafkaConsumerWrapper, storage: Redis):
                self._consumer = consumer
                self._storage = storage

            async def on_partitions_revoked(self, revoked: list[TopicPartition]) -> None:
                if self._consumer.current_offset:
                    await self._storage.mset(
                        mapping={str(tp.partition): offset for tp, offset in self._consumer.current_offset.items()}
                    )

            async def on_partitions_assigned(self, assigned: list[TopicPartition]) -> None:
                self._consumer._current_offset = {}
                for tp in assigned:
                    offset = await self._storage.get(tp.partition)
                    if offset is not None:
                        self._consumer.seek(tp, int(offset))
                        self._consumer.set_current_offset(tp, int(offset))

        self.subscribe(topics=self._topics, listener=SafeRebalancerListener(self, self._storage))

    async def save_offset_to_storage(self, key: str, value: int):
        await self._storage.set(key, value)

    async def save_and_commit_offset(self, offset: int, partition: int, topic: str):
        self.set_current_offset(key=TopicPartition(topic, partition), value=offset + 1)
        await self.save_offset_to_storage(str(partition), offset + 1)
        await self.commit(self.current_offset)

    @property
    def current_offset(self) -> Dict[TopicPartition, int]:
        return self._current_offset

    def set_current_offset(self, key: TopicPartition, value: int):
        self._current_offset[key] = value


async def start_consumer_worker() -> AIOKafkaConsumerWrapper:
    consumer = AIOKafkaConsumerWrapper(
        redis_db=1,
        redis_url="redis://redis/0",
        topics=[settings["KAFKA"]["Topic"]],
        bootstrap_servers=settings["KAFKA"]["Host"],
        group_id="custom-group-id",
        key_deserializer=bytes.decode,
        value_deserializer=lambda x: json.loads(x.decode()),
        enable_auto_commit=False,
    )
    consumer.subscribe_and_set_rebalancer()
    await consumer.start()
    return consumer


async def start_consume():
    repository = SQLAlchemyRepository(get_session())
    consumer = await start_consumer_worker()
    try:
        while True:
            record = await consumer.getone()
            for skill in record.value:
                skill_obj = await repository.get_or_create_skill(name=skill)
                position = await repository.get_position(record.key)
                existing_position_skill = await repository.position_skill_exists(position, skill_obj)
                if existing_position_skill is not None:
                    await repository.update_position_skill(existing_position_skill)
                else:
                    await repository.add_position_skill(models.PositionSkill(skill_obj.id, position.id))
            await consumer.commit(consumer.current_offset or None)
    finally:
        await consumer.commit(consumer.current_offset or None)
        await consumer.stop()
