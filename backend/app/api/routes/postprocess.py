"""Manual post-processing routes."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.postprocessing import run_completed_downloads, run_folder

router = APIRouter(prefix="/postprocess", tags=["postprocess"])


class ProcessResultOut(BaseModel):
    release: str
    status: str
    message: str
    destination: str | None = None


class FolderIn(BaseModel):
    path: str


@router.post("/run", response_model=list[ProcessResultOut])
async def run_completed(db: DbSession, _: CurrentUser):
    """File everything SABnzbd has finished downloading."""
    results = await run_completed_downloads(db)
    return [ProcessResultOut(**r.__dict__) for r in results]


@router.post("/folder", response_model=list[ProcessResultOut])
async def run_for_folder(payload: FolderIn, db: DbSession, _: CurrentUser):
    """Process a specific folder of downloaded files."""
    results = await run_folder(db, payload.path)
    return [ProcessResultOut(**r.__dict__) for r in results]
