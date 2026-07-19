from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.core.database import BaseModel as ORMBaseModel

ModelType = TypeVar("ModelType", bound=ORMBaseModel)
SchemaType = TypeVar("SchemaType")


class CursorPageParams(BaseModel):
    cursor: str | None = Field(default=None, examples=["01K8X...abc"])
    limit: int = Field(default=20, ge=1, le=100)


class CursorPage(BaseModel, Generic[SchemaType]):
    items: list[SchemaType]
    next_cursor: str | None


async def paginate_by_cursor(
    db: AsyncSession,
    stmt: Select[tuple[ModelType]],
    id_column: InstrumentedAttribute[str],
    params: CursorPageParams,
) -> tuple[list[ModelType], str | None]:
    if params.cursor is not None:
        stmt = stmt.where(id_column < params.cursor)
    stmt = stmt.order_by(id_column.desc()).limit(params.limit + 1)

    result = await db.execute(stmt)
    items = list(result.scalars().all())

    next_cursor = None
    if len(items) > params.limit:
        items = items[: params.limit]
        next_cursor = items[-1].id

    return items, next_cursor
