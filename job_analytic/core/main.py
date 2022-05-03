import asyncio
from typing import List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from adapters import orm, schemas
from adapters.repository import SQLAlchemyRepository
from db.config import get_session
from domain import models
from service_layer.queue.consumer import start_consume
from service_layer.resources.pool import ResourcePool
from service_layer.sync import start_sync


app = FastAPI(title="Job Analytic")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    asyncio.ensure_future(start_consume())
    orm.configure_mappers()


@app.get("/api/v1/positions", response_model=List[schemas.Position])
async def get_positions(session: AsyncSession = Depends(get_session)):
    repository = SQLAlchemyRepository(session)
    return await repository.get_positions()


@app.get("/api/v1/get-stats/{query}", response_model=List[schemas.PositionSkill])
async def get_stats(query: str, session: AsyncSession = Depends(get_session)) -> List[models.PositionSkill]:
    repository = SQLAlchemyRepository(session)
    return await repository.get_position_skills(query)


@app.post("/app/v1/sync")
async def invoke_synchronization(session: AsyncSession = Depends(get_session)):
    repository = SQLAlchemyRepository(session)
    asyncio.ensure_future(start_sync(session))
    return {"positions": list(map(lambda x: x.name, await repository.get_positions()))}


@app.on_event("shutdown")
async def on_shutdown():
    await asyncio.wait([task for task in asyncio.all_tasks()], timeout=10)

    http_session = ResourcePool().http_session
    http_session.close()
