from fastapi import APIRouter
from sqlalchemy import text

from app.api.dependencies import DBDep

router = APIRouter(prefix="/handlers", tags=["handlers ⚙⚙⚙"])


@router.get("/check_db")
async def check_db(uow: DBDep):
    res = await uow.execute(text("SELECT VERSION ()"))
    return {"version": res.scalar()}
