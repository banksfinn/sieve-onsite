from typing import Generic, TypeVar

from fullstack_types.datetimes import AnnotatedArrow
from fullstack_types.query import DEFAULT_LIMIT, DEFAULT_OFFSET, SortOrder
from pydantic import BaseModel
from sqlalchemy import Integer, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm._orm_constructors import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.sqltypes import DateTime


class BaseEntityModel(DeclarativeBase):
    """
    The base unit for our database entities.
    """

    __abstract__ = True

    # The primary key for the entity
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Created at and updated at timestamps, automatically set by the database
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self, exclude: set[str] | None = None):
        """
        Convert the entity to a dictionary.
        """
        if not exclude:
            exclude = set()
        return {column.name: getattr(self, column.name) for column in self.__table__.columns if column.name not in exclude}


class BaseEntity(BaseModel):
    id: int
    created_at: AnnotatedArrow
    updated_at: AnnotatedArrow


class BaseEntityQuery(BaseModel):
    limit: int = DEFAULT_LIMIT
    offset: int = DEFAULT_OFFSET

    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.desc


class BaseEntityCreateRequest(BaseModel):
    pass


class BaseEntityUpdateRequest(BaseModel):
    id: int


class BaseEntityDeleteRequest(BaseModel):
    id: int


class SearchResponseMetadata(BaseModel):
    total_count: int
    limit: int
    offset: int


BaseEntityModelType = TypeVar("BaseEntityModelType", bound=BaseEntityModel)
BaseEntityType = TypeVar("BaseEntityType", bound=BaseEntity)
BaseEntityQueryType = TypeVar("BaseEntityQueryType", bound=BaseEntityQuery)
BaseEntityCreateRequestType = TypeVar("BaseEntityCreateRequestType", bound=BaseEntityCreateRequest)
BaseEntityUpdateRequestType = TypeVar("BaseEntityUpdateRequestType", bound=BaseEntityUpdateRequest)
BaseEntityDeleteRequestType = TypeVar("BaseEntityDeleteRequestType", bound=BaseEntityDeleteRequest)


class BaseEntitySearchResponse(BaseModel, Generic[BaseEntityType]):
    entities: list[BaseEntityType]
    metadata: SearchResponseMetadata
