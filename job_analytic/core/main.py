import asyncio
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_analytic.adapters import schemas, orm
from job_analytic.adapters.repository import SQLAlchemyRepository
from job_analytic.db.config import SessionLocal
from job_analytic.domain import models
from job_analytic.service_layer.queue.consumer import start_consume
from job_analytic.service_layer import api
from job_analytic.service_layer.sync import start_sync

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
    orm.configure_mappers()


@app.get("/api/v1/positions", response_model=list[schemas.Position])
def get_positions() -> List[models.Position]:
    return api.get_positions()


@app.get("/api/v1/get-stats/{query}", response_model=list[schemas.PositionSkill])
def get_stats(query: str) -> List[models.PositionSkill]:
    return api.get_report(query)


@app.post("/app/v1/sync")
async def invoke_synchronization():
    db = SessionLocal()
    repository = SQLAlchemyRepository(db)
    for _ in range(2):
        asyncio.ensure_future(start_consume())
    asyncio.ensure_future(start_sync())
    return {"positions": list(map(lambda x: x.name, repository.list_positions()))}
